#!/usr/bin/env python

"""
Face tagger

Usage:
  tag-faces [-s <dir>] add [--load-faces] <input>...
  tag-faces [-s <dir>] extract
  tag-faces [-s <dir>] extract inspect [--all]
  tag-faces [-s <dir>] extract erase
  tag-faces [-s <dir>] tag
  tag-faces [-s <dir>] tag inspect [--all]
  tag-faces [-s <dir>] embed
  tag-faces (-h | --help)

Commands:
  add              Add given pictures to index.
  extract          Extract all faces in index.
  extract inspect  Show extracted faces surimposed on original pictures.
  reset            Remove all detected faces.
  tag              Recognize faces in index.
  tag inspect      Show tagged faces surimposed on original pictures.
  embed            Embed tags in pictures from index.

<input> is either a file, a folder or a glob pattern.
Examples:
  path/to/file.jpg
  path/to/folder
  /path/to/files*
  /path/**/files*

Options:
  -s --settings-dir <dir>  casc xml file [default: ~/.mFPN-organizer/]
  --load-faces             load faces contained in files
  --all                    show all pictures, not those only with faces
  -h --help                this help message
"""

# yaourt opencv ffmpeg
# sudo pip2 install numpy
# sudo pip2 install docopt
# sudo apt-get install libopencv-dev python-opencv

import os
import sqlite3
import sys

import cv2
from docopt import docopt

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import utils  #pylint: disable=import-error,wrong-import-position


def main(argv=None):
    args = docopt(__doc__, argv=argv)

    settings_dir = os.path.expanduser(args['--settings-dir'])
    utils.mkdir_p(settings_dir)
    db = os.path.join(settings_dir, 'pictures.db')

    if args['add']:
        pictures = utils.get_all_files(args['<input>'])
        add_pictures(db, pictures)
    elif args['extract']:
        if args['inspect']:
            inspect_extracted_faces(db, args['--all'])
        elif args['erase']:
            erase_extracted_faces(db)
        else:
            casc_files = list(utils.get_all_files(os.path.join(settings_dir, 'casc', 'frontal')))
            extract_faces(casc_files, db)
    elif args['reset']:
        reset_faces(db)
    elif args['tag']:
        if args['inspect']:
            pass#inspect_tagged_faces(db, args[--all])
        else:
            pass#tag_faces(db)
    elif args['embed']:
        pass#embed_tags(db)


def create_tables(conn):
    c = conn.cursor()

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS picture (
            file TEXT NOT NULL,
            file_hash TEXT NOT NULL,
            w INTEGER NOT NULL,
            h INTEGER NOT NULL,
            faces_approved INTEGER NOT NULL DEFAULT 0,
            UNIQUE(file, w, h)
        );
        ''')

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS face (
            picture_rowid TEXT NOT NULL,
            user_name TEXT,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            w INTEGER NOT NULL,
            h INTEGER NOT NULL,
            approved INTEGER NOT NULL DEFAULT 0,
            UNIQUE(picture_rowid, x, y, w, h)
        );
        ''')

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS user (
            name TEXT PRIMARY KEY,
            metadata TEXT
        );
        ''')

    conn.commit()


def get_pictures(conn, columns=None, only_not_approved=False):
    columns = columns or ['rowid', 'file', 'file_hash', 'w', 'h']

    c = conn.cursor()

    return c.execute(
        '''
        SELECT {columns}
        FROM picture
        {where}
        ORDER BY file;
        '''.format(
            columns=','.join(columns),
            where='WHERE faces_approved = 0' if only_not_approved else '',
        )).fetchall()


def get_faces_for_file(conn, picture_rowid):
    c = conn.cursor()

    return c.execute(
        '''
        SELECT x, y, w, h FROM face
        WHERE picture_rowid = ?;
        ''',
        [picture_rowid]
    ).fetchall()


def replace_faces_for_file(conn, picture_rowid, faces, approve=False):
    c = conn.cursor()

    c.execute(
        '''
        DELETE FROM face
        WHERE picture_rowid = ?;
        ''',
        [picture_rowid]
    )

    for x, y, w, h in faces:
        sql_values = utils.sql.build_values((picture_rowid, x, y, w, h, approve))
        c.execute(
            '''
            INSERT INTO face (picture_rowid, x, y, w, h, approved)
            {values};
            '''.format(
                values=sql_values
            )
        )

    if approve:
        c.execute(
            '''
            UPDATE picture SET faces_approved = 1
            WHERE rowid = ?;
            ''',
            [picture_rowid]
        )

    conn.commit()


def add_pictures(db, pictures):
    conn = sqlite3.connect(db)
    create_tables(conn)

    sql = '''
    INSERT INTO picture (file, file_hash, w, h)
    {values}
    '''

    for path in pictures:
        try:
            complete_path = os.path.abspath(path)
            md5 = utils.md5(path)
            image = cv2.imread(path)
            width, height = utils.cv2.get_size(image)

            sql_values = utils.sql.build_values((complete_path, md5, width, height))
            conn.execute(sql.format(values=sql_values))
            conn.commit()
        except Exception as e:
            print 'Warning, did not add file {}: {}'.format(path, e)


def extract_faces(casc_files, db):
    conn = sqlite3.connect(db)

    face_sql = '''
    INSERT INTO face (picture_rowid, x, y, w, h)
    {values};
    '''

    for rowid, path, width, height in get_pictures(conn, ['rowid', 'file', 'w', 'h'], only_not_approved=True):
        faces = detect_faces(casc_files, path, width, height)
        for (x, y, w, h) in faces:
            sql_values = utils.sql.build_values((rowid, x, y, w, h))
            try:
                conn.execute(face_sql.format(values=sql_values))
                conn.commit()
            except sqlite3.IntegrityError:
                pass

        conn.commit()
        print 'found {} faces in {}'.format(len(faces), path)

    conn.close()


def reset_faces(db):
    conn = sqlite3.connect(db)

    face_sql = '''
    DELETE FROM face;
    '''

    conn.execute(face_sql)
    conn.commit()


def detect_faces(casc_files, path, width, height):
    face_cascades = [cv2.CascadeClassifier(casc) for casc in casc_files]
    gray = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2GRAY)

    min_length = min(width/30, height/30)

    all_faces = [casc.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(min_length, min_length),
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    ) for casc in face_cascades]


    faces = [f for faces in all_faces for f in faces]
    faces, _ = cv2.groupRectangles(faces, 2)
    return faces


def inspect_extracted_faces(db, show_all=False):
    max_size = 640, 640

    conn = sqlite3.connect(db)

    all_files = get_pictures(conn, ['rowid', 'file'], only_not_approved=not show_all)
    for i, (rowid, path) in enumerate(all_files, 1):
        image = cv2.imread(path)

        faces = get_faces_for_file(conn, rowid)

        window_name = "Faces found"
        image_name = "[%d/%d] %d %s" % (i, len(all_files), rowid, path)
        pic = PictureWithRectangles(window_name, image_name, image, faces, max_size)
        save = pic.show()
        if save:
            replace_faces_for_file(conn, rowid, pic.rectangles['permanent'], approve=True)


def erase_extracted_faces(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('DELETE FROM face;')


class AddMouseAction(utils.cv2.MouseButtonAction):
    def __init__(self, rectangles):
        self.rectangles = rectangles
        self.mouse_down_point = None

    def _handle_down(self, x, y):
        self.mouse_down_point = (x, y)
        return True

    def _handle_move(self, x, y):
        if not self.mouse_down_point:
            return False
        x_0, y_0 = self.mouse_down_point
        x_0, y_0, x, y = (min(x_0, x), min(y_0, y), max(x_0, x), max(y_0, y))
        rectangle = (x_0, y_0, x - x_0, y - y_0)
        self.rectangles['adding'] = rectangle
        return True

    def _handle_up(self, x, y):  # pylint: disable=unused-argument
        self.mouse_down_point = None
        if self.rectangles['adding']:
            self.rectangles['permanent'].append(self.rectangles['adding'])
            self.rectangles['adding'] = None
        return True


class RemoveMouseAction(utils.cv2.MouseButtonAction):
    def __init__(self, rectangles):
        self.rectangles = rectangles

    def _handle_move(self, x, y):  # pylint: disable=unused-argument
        self.rectangles['in_deletion'] = self.rectangles['inside']
        return True

    def _handle_up(self, x, y):  # pylint: disable=unused-argument
        if self.rectangles['inside'] is not None:
            del self.rectangles['permanent'][self.rectangles['inside']]
            self.rectangles['inside'] = None
            self.rectangles['in_deletion'] = None
            return True

    def _handle_stop(self, x, y):  # pylint: disable=unused-argument
        self.rectangles['in_deletion'] = None


class MoveMouseAction(utils.cv2.MouseButtonAction):
    def __init__(self, rectangles):
        self.rectangles = rectangles
        self.move = False
        self.last_x = None
        self.last_y = None

    def _handle_down(self, x, y):
        self.rectangles['moving'] = self.rectangles['inside']
        self.move = True
        self.last_x = x
        self.last_y = y

    def _handle_move(self, x, y):
        if not self.move:
            self.rectangles['moving'] = self.rectangles['inside']
        else:
            old_x, old_y, w, h = self.rectangles['permanent'][self.rectangles['moving']]
            new_x, new_y = (old_x + x - self.last_x), (old_y + y - self.last_y)
            self.rectangles['permanent'][self.rectangles['moving']] = (new_x, new_y, w, h)
        self.last_x = x
        self.last_y = y

    def _handle_up(self, x, y):  # pylint: disable=unused-argument
        self.move = False
        self.last_x = None
        self.last_y = None

    def _handle_stop(self, x, y):  # pylint: disable=unused-argument
        self.move = False
        self.last_x = None
        self.last_y = None


class PictureWithRectangles(object):
    """Handle inputs for pictures with rectangles.

    Clicking and dragging creates a rectangle.
    Ctrl-clicking removes a rectangle.
    Shift-clicking moves a rectangle.

    Escape cancel changes.
    Enter accept changes.
    """
    def __init__(self, window, image_title, image, rectangles=None, max_size=None):
        self.window = window
        self.image_title = image_title
        self.image = image
        self.rectangles = {
            'permanent': rectangles or [],
            'adding': None,
            'moving': None,
            'in_deletion': None,
            'inside': None,
        }
        self.max_size = max_size

        self.actions = {
            None: AddMouseAction(self.rectangles),
            cv2.EVENT_FLAG_CTRLKEY: RemoveMouseAction(self.rectangles),
            cv2.EVENT_FLAG_SHIFTKEY: MoveMouseAction(self.rectangles),
        }
        self.action_state = None

        self.usage = 'Enter | Escape | Ctrl-C | Click & Drag | Ctrl Click | Shift Click'

    def show(self):
        self._create_window()

        key = None
        while key not in [utils.cv2.EVENT_KEY_ESCAPE,
                          utils.cv2.EVENT_KEY_CTRL_C,
                          utils.cv2.EVENT_KEY_ENTER]:
            self._show_image()
            key = cv2.waitKey(100)

        if key == utils.cv2.EVENT_KEY_ESCAPE:
            return False
        elif key == utils.cv2.EVENT_KEY_CTRL_C:
            exit()
        elif key == utils.cv2.EVENT_KEY_ENTER:
            return True

    def _show_image(self):
        image = self.image.copy()

        for i, (x, y, w, h) in enumerate(self.rectangles['permanent']):
            if i == self.rectangles['moving']:
                color = (255, 0, 0)
            elif i == self.rectangles['in_deletion']:
                color = (0, 0, 255)
            else:
                color = (0, 255, 0)
            cv2.rectangle(image, (x, y), (x+w, y+h), color, 10)

        if self.rectangles['adding']:
            x, y, w, h = self.rectangles['adding']  #pylint: disable=unpacking-non-sequence
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 10)

        utils.cv2.display_text_width(image, self.image_title, cv2.FONT_HERSHEY_PLAIN, (255, 255, 255), (25, 25, 25), 3, 10, align_top_left=True)
        utils.cv2.display_text_width(image, self.usage, cv2.FONT_HERSHEY_PLAIN, (255, 255, 255), (50, 50, 50), 3, 10, align_bottom_left=True)
        cv2.imshow(self.window, image)

    def _create_window(self):
        cv2.namedWindow(self.window, cv2.WINDOW_NORMAL)
        if self.max_size:
            cv2.resizeWindow(self.window, self.max_size[0], self.max_size[1])
        cv2.setMouseCallback(self.window, self._handle_mouse)

    def _handle_mouse(self, event, x, y, flags, param):  # pylint: disable=unused-argument
        if event == cv2.EVENT_MOUSEMOVE:
            self.rectangles['inside'] = self._compute_inside_rectangle(x, y)

        if event == cv2.EVENT_LBUTTONDOWN:
            self.action_state = 'down'
        elif event == cv2.EVENT_MOUSEMOVE:
            self.action_state = 'move'
        elif event == cv2.EVENT_LBUTTONUP:
            self.action_state = 'up'
        else:
            self.action_state = 'stop'

        has_action = False
        for flag, callback in self.actions.iteritems():
            if flag is not None and flags & flag:
                has_action = True
                callback(self.action_state, x, y)
        if not has_action and self.actions.get(None):
            self.actions[None](self.action_state, x, y)  # pylint: disable=not-callable

    def _compute_inside_rectangle(self, x_0, y_0):
        best_score = None
        best_index = None
        for i, (x, y, w, h) in enumerate(self.rectangles['permanent']):
            inside = x < x_0 < x + w and y < y_0 < y + h
            if inside:
                score = w + h
                if best_score is None or score < best_score:
                    best_score = score
                    best_index = i
        return best_index


if __name__ == '__main__':
    main()
