import os
import sys
import time

import pylink as pl
from experiment.constants import COLOR, INSTRUCTIONS_FONT_SIZE
from psychos.visual import Circle, Text
from experiment.PsychosCustomDisplay import PsychosCustomDisplay
from math import sin, cos, pi, atan, sqrt, radians, hypot

RIGHT_EYE = 1
LEFT_EYE  = 0
BINOCULAR = 2

def _try_connection():
    """Attempts to connect to eyetracker.
    Returns a bool indicating if a connection was made and an exception if applicable.
    If there's no exeception, the second return value will be None.
    """
    print('Attempting to connect to eye tracker...')
    try:
        pl.EyeLink()
        return True, None
    except RuntimeError as e:
        return False, e

def _display_not_connected_text(window):
    """Displays the text objects describing available interactions.
    
    Parameters:
    window -- a psychopy.visual.Window
    """
    warning_text = ('WARNING: Eyetracker not connected.\n\n'
                    'Press "R" to retry connecting\n'
                    'Press "Q" to quit\n'
                    'Press "D" to continue in debug mode')

    text_widget = Text(text=warning_text, font_size=INSTRUCTIONS_FONT_SIZE, color=COLOR, position=(960,540))
    text_widget.draw()
    window.flip()
    #window.flip(clearBuffer=False)


def _get_connection_failure_response(window):
    """Returns a key press."""
    key_event = window.wait_key(['r', 'q', 'd'])
    key = key_event.key
    return key

        
def EyeLinker(window, filename, eye):
    connected, e = _try_connection()

    if connected:
        return ConnectedEyeLinker(window, filename, eye, text_color=COLOR)
    else:
        _display_not_connected_text(window)
        response = _get_connection_failure_response(window)
        print('Response:', response)
        while response == 'R':
            connected, e = _try_connection()
            if connected:
                window.flip()
                return ConnectedEyeLinker(window, filename, eye, text_color=None)
            else:
                print('Could not connect to tracker. Select again.')
                response = _get_connection_failure_response(window)  # Fixed: Passing window here

        if response == 'Q':
            window.flip()
            raise e
        elif response == 'D':
            window.flip()
            print('Continuing with mock eyetracking. Eyetracking data will not be saved!')
            return MockEyeLinker(window, filename, eye, text_color=None)
        else:
            # Optionally reprompt or return a safe default
            window.flip()
            print('Unexpected key response. Defaulting to debug mode.')
            return MockEyeLinker(window, filename, eye, text_color=None)

    
class ConnectedEyeLinker:
    """Returned if a connection is possible."""
    def __init__(self, window, filename, eye, text_color=None):
        """See Eyelinker factory function for parameter info."""
        if len(filename) > 12:
            raise ValueError(
                'EDF filename must be at most 12 characters long including the extension.')

        if filename[-4:] != '.edf':
            raise ValueError(
                'Please include the .edf extension in the filename.')

        if eye not in ('LEFT', 'RIGHT', 'BOTH'):
            raise ValueError('eye must be set to LEFT, RIGHT, or BOTH.')

        self.window = window
        self.edf_filename = filename
        self.edf_open = False
        self.eye = eye
        self.resolution = tuple(window.size)
        self.tracker = pl.EyeLink()
        self.genv = PsychosCustomDisplay(self.window, self.tracker)
        self.mock = False

        if text_color is None:
            if all(i >= 0.5 for i in self.window.color):
                self.text_color = (0, 0, 0)
            else:
                self.text_color = (1, 1, 1)
        else:
            self.text_color = text_color

    def initialize_graphics(self):
        """Opens the PsychoPyCustomDisplay object.
        Must be called during setup phase.
        """
        self.set_offline_mode()
        pl.openGraphicsEx(self.genv)

    def initialize_tracker(self):
        """Sends commands setting up basic settings that are unlikely to be changed.
        EDF file must be open before this function is called. Must be called before
        starting to record.
        """
        if not self.edf_open:
            raise RuntimeError('EDF file must be open before tracker can be initialized.')

        pl.flushGetkeyQueue()
        self.set_offline_mode()

        self.send_command("screen_pixel_coords = 0 0 %d %d" % (self.window.width-1, self.window.height-1)) # % self.resolution
        self.send_message("DISPLAY_COORDS 0 0 %d %d" % (self.window.width-1, self.window.height-1)) # % self.resolution

        self.tracker.setFileEventFilter(
            "LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
        self.tracker.setFileSampleFilter(
            "LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")
        self.tracker.setLinkEventFilter(
            "LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
        self.tracker.setLinkSampleFilter(
            "LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")

    def send_tracking_settings(self, settings=None):

        """Sends settings to tracker.
        Default settings are sent, but can be overwritten.
        Parameters:
        settings -- a dictionary of settings to overwrite the defaults.
        For information about settings, see the pylink docs.
        """
        defaults = {
            'automatic_calibration_pacing': 1000,
            'background_color': (0, 0, 0),
            'calibration_area_proportion': (0.7, 0.7),
            'calibration_type': 'HV9',
            'elcl_configuration': 'BTABLER',
            'enable_automatic_calibration': 'YES',
            'error_sound': '',
            'foreground_color': (255, 255, 255),
            'good_sound': '',
            'preamble_text': None,
            'pupil_size_diameter': 'NO',
            'saccade_acceleration_threshold': 9500,
            'saccade_motion_threshold': 0.15,
            'saccade_pursuit_fixup': 60,
            'saccade_velocity_threshold': 30,
            'sample_rate': 1000,
            'target_sound': '',
            'validation_area_proportion': (0.7, 0.7),
        }

        if settings is None:
            settings = {}

        defaults.update(settings)
        settings = defaults

        self.send_command('elcl_select_configuration = %s' % settings['elcl_configuration'])

        #pl.setCalibrationColors(settings['foreground_color'], settings['background_color'])
        #pl.setCalibrationSounds(
        #    settings['target_sound'], settings['good_sound'], settings['error_sound'])

        if self.eye in ('LEFT', 'RIGHT'):
            self.send_command('active_eye = %s' % self.eye)

        self.send_command(
            'automatic_calibration_pacing = %i' % settings['automatic_calibration_pacing'])

        if self.eye == 'BOTH':
            self.send_command('binocular_enabled = YES')
        else:
            self.send_command('binocular_enabled = NO')

        self.send_command('calibration_area_proportion %f %f' % settings['calibration_area_proportion'])
        
        self.send_command('calibration_type = %s' % settings['calibration_type'])
        self.send_command(
            'enable_automatic_calibration = %s' % settings['enable_automatic_calibration'])
        if settings['preamble_text'] is not None:
            self.send_command('add_file_preamble_text %s' % '"' + settings['preamble_text'] + '"')
        self.send_command('pupil_size_diameter = %s' % settings['pupil_size_diameter'])
        self.send_command(
            'saccade_acceleration_threshold = %i' % settings['saccade_acceleration_threshold'])
        self.send_command('saccade_motion_threshold = %i' % settings['saccade_motion_threshold'])
        self.send_command('saccade_pursuit_fixup = %i' % settings['saccade_pursuit_fixup'])
        self.send_command(
            'saccade_velocity_threshold = %i' % settings['saccade_velocity_threshold'])
        self.send_command('sample_rate = %i' % settings['sample_rate'])
        self.send_command('validation_area_proportion %f %f' % settings['validation_area_proportion'])
    def open_edf(self):
        """Opens the edf file, must be called before tracker is initialized."""
        self.tracker.openDataFile(self.edf_filename)
        self.edf_open = True

    def close_edf(self):
        """Closes the edf file at the end of the experiment."""
        self.tracker.closeDataFile()
        self.edf_open = False

    def transfer_edf(self, new_filename=None):
        """Transfers the edf file to the computer running psychopy.
        Parameters:
        new_filename -- optionally, a new filename for the edf file with no character restriciton.
        """
        if not new_filename:
            new_filename = self.edf_filename

        if new_filename[-4:] != '.edf':
            raise ValueError('Please include the .edf extension in the filename.')

        # Prevents timeouts due to excessive printing
        sys.stdout = open(os.devnull, "w")
        self.tracker.receiveDataFile(self.edf_filename, new_filename)
        sys.stdout = sys.__stdout__
        print(new_filename + ' has been transferred successfully.')

    def setup_tracker(self):
        """Enters setup menu on eyelink computer."""
        self.window.flip()
        self.tracker.doTrackerSetup()

    def display_eyetracking_instructions(self): # CALIBRATION INSTRUCTIONS
        """Displays basic instructions to participant."""
        self.window.flip()

        Circle(radius=18, color='white', position=(self.window.width*0.5, self.window.height * 0.5), window=self.window).draw()
        Circle(radius=6, color='black', position=(self.window.width*0.5, self.window.height * 0.5), window=self.window).draw()

        Text(
            text='Sometimes a target that looks like this will appear.',
            font_size=INSTRUCTIONS_FONT_SIZE, color=COLOR, position=(self.window.width*0.5, self.window.height * 0.58), window=self.window
        ).draw()

        Text(
            text='We use it to calibrate the eye tracker. Stare at it whenever you see it.',
            font_size=INSTRUCTIONS_FONT_SIZE, color=COLOR, position=(self.window.width*0.5, self.window.height * 0.46), window=self.window
        ).draw()

        Text(
            text='Press space to continue.',
            font_size=INSTRUCTIONS_FONT_SIZE, color=COLOR, position=(self.window.width*0.5, self.window.height * 0.42), window=self.window

        ).draw(),

        self.window.flip()
        self.window.wait_key(['space'])
        self.window.flip()

    def calibrate(self, text=None):
        """Like setup_tracker, but gives the experimenter the option to skip.
        Parameters:
        text -- A string containing the text to display to the experimenter
        """
        self.window.flip()

        if text is None:
            text = (
               "Notify experimenter to calibrate the equipment."
            )

        Text(
            text=text, font_size=INSTRUCTIONS_FONT_SIZE, color=COLOR, position=(self.window.width*0.5, self.window.height * 0.5), window=self.window
        ).draw()

        self.window.flip()
        self.window.wait_key(['space'])
        self.tracker.doTrackerSetup()
        

    def drift_correct(self, position=None, setup=1):
        """Enters into drift correct mode.
        Parameters:
        position -- A 2 item tuple describing where the target should be displayed in window units
        setup -- If the setup menu should be accessed after correction
        """
        if position is None:
            position = tuple([int(round(i/2)) for i in self.resolution])

        try:
            self.tracker.doDriftCorrect(position[0], position[1], 1, setup)
            self.tracker.applyDriftCorrect()
        except RuntimeError as e:
            print(e.message)

    def record(self, to_record_func):
        """A python decorator for if what you want to record is contained in a single function.
        See eyelinker_example.py for an example."""
        def wrapped_func():
            self.start_recording()
            to_record_func()
            self.stop_recording()
        return wrapped_func

    def start_recording(self):
        """Start the eyetracking recording.
        Requires a short delay after calling, so do not call this function during a timing
         specific part of the experiment.
        """
        self.tracker.startRecording(1, 1, 1, 1)
        time.sleep(.1)  # required

    def stop_recording(self):
        """Stops the eyetracking recording.
        Requires a short delay before calling, so do not call this function during a timing
         specific part of the experiment.
        """
        time.sleep(.1)  # required
        self.tracker.stopRecording()

    @property
    def gaze_data(self):
        """A property with the most recent gaze sample.
        Contains a tuple with gaze data. If both eyes are being tracked the tuple contains two
         tuples. Each tuple of gaze data contains an x and y value in pixels. Can be accessed
         with `tracker.gaze_data`
        See eyelinker_example.py for an example.
        """
        sample = self.tracker.getNewestSample()

        if self.eye == 'LEFT':
            return sample.getLeftEye().getGaze()
        elif self.eye == 'RIGHT':
            return sample.getRightEye().getGaze()
        else:
            return (sample.getLeftEye().getGaze(), sample.getRightEye().getGaze())

    @property
    def pupil_size(self):
        """A property with the most recent pupil size.
        If both eyes are being tracked, returns a tuple containing two values. Otherwise, returns
        a single value. Pupil sizes units can be controlled with `send_tracking_settings`.
         Eyelinker returns area by defult. See pylink docs about `setPupilSizeDiameter` for more
         info.
        See eyelinker_example.py for an example.
        """
        sample = self.tracker.getNewestSample()

        if self.eye == 'LEFT':
            return sample.getLeftEye().getPupilSize()
        elif self.eye == 'RIGHT':
            return sample.getRightEye().getPupilSize()
        else:
            return (sample.getLeftEye().getPupilSize(), sample.getRightEye().getPupilSize())

    def set_offline_mode(self):
        """Sets tracker to offline mode."""
        self.tracker.setOfflineMode()

    def send_command(self, cmd):
        """Sends a command to the tracker.
        Mostly used internally, but available if needed. See pylink docs for available commands.
        Parameters:
        cmd -- A string containing the command to be send to the tracker
        """
        self.tracker.sendCommand(cmd)

    def send_message(self, msg):
        """Sends a message to be saved to the EDF file.
        Not to be confused with send_status. Useful for marking specific times, e.g. trial start
        Parameters:
        msg -- A string containing information to be saved.
        """
        self.tracker.sendMessage(msg)

    def send_status(self, status):
        """Sends a status to be displayed to the experimenter.
        The status is displayed on the eyelink computer during the experiment. Useful for tracking
         information like the current experiment condition during recording.
        Parameters:
        status -- A string containing the info to be displayed. Should be less than 80 characters.
        """

        if len(status) >= 80:
            print('Warning: Status should be less than 80 characters.')

        self.send_command("record_status_message '%s'" % status)

    def close_connection(self):
        """Closes the connection to the tracker.
        Must be called at the end of the experiment."""
        self.tracker.close()
        pl.closeGraphics()

    def end_exp(self):
        """end Experiment, close and transfer the file"""

        self.stop_recording()
        self.close_edf()
        self.transfer_edf()
        self.close_connection()

        print('Clean up tests passed...')
    
    def init_tracker(self):
        # initialize
        self.initialize_graphics()
        self.open_edf()
        self.initialize_tracker()
        self.send_tracking_settings()
        print('Initalization tests passed...')

    def testFunAndCalib(self):
        """Closes the connection to the tracker.
        Must be called at the end of the experiment."""

        self.display_eyetracking_instructions()

        self.calibrate()  # choice given
        self.send_status('Recording...')
        self.send_message('test_message')
        self.start_recording()
        time.sleep(2)
        self.stop_recording()
        print('Basic functionality tests passed...')

def topLeftToCenter(pointXY, screenXY, flipY=False):
    """
    Takes a coordinate given in topLeft reference frame and transforms it
    to center-based coordiantes. Switches from (0,0) as top left to
    (0,0) as center
    Parameters
    ----------
    pointXY : tuple
        The topLeft coordinate which is to be transformed
    screenXY : tuple, ints
        The (x,y) dimensions of the grid or screen
    flipY : Bool
        If True, flips the y coordinates
    Returns
    -------
    newPos : tuple
        The (x,y) position in center-based coordinates
    Examples
    --------
    >>> newPos = topLeftToCenter((100,100), (1920,1080), False)
    >>> newPos
    (-860.0, 440.0)
    """
    newX = pointXY[0] - (screenXY[0] / 2.0)
    newY = (screenXY[1] / 2.0) - pointXY[1]
    if flipY:
        newY *= -1
    return [newX, newY]


def centerToTopLeft(pointXY, screenXY, flipY=False):
    """
    Takes a coordinate given in a centered reference frame and transforms it
    to topLeft based coordiantes. Switches from (0,0) as center to
    (0,0) as topLeft
    Parameters
    ----------
    pointXY : tuple
        The center-based coordinate which is to be transformed
    screenXY : tuple, ints
        The (x,y) dimensions of the grid or screen
    flipY : Bool
        If True, flips the y coordinates
    Returns
    -------
    newPos : tuple
        The (x,y) position in topLeft based coordinates
    Examples
    --------
    >>> newPos = centerToTopLeft((100,100), (1920,1080), False)
    >>> newPos
    (1060, 640)
    """
    
    newX = pointXY[0] + (screenXY[0] / 2)
    if not flipY:
        newY = pointXY[1] + (screenXY[1] / 2)
    else:
        newY = (pointXY[1] * -1) + (screenXY[1] / 2)
    return [newX, newY]


def check_sacc(Dis_sacc, startime = 0):

    ''' check for eye movements'''
    
    # check recording eye
    eye_used = pl.getEYELINK().eyeAvailable(); #determine which eye(s) are available 
    if eye_used == LEFT_EYE or eye_used == BINOCULAR: eye_used = LEFT_EYE

    gotSac = False

    d = pl.getEYELINK().getNextData()
    if (d == 6) and (not gotSac):
        newEvent = pl.getEYELINK().getFloatData()
        if newEvent and (eye_used == newEvent.getEye()):
            startLoc   = newEvent.getStartGaze()
            endLoc     = newEvent.getEndGaze()
            sacDist    = sqrt((startLoc[0] - endLoc[0])**2 + (startLoc[1] - endLoc[1])**2)
            if sacDist >=Dis_sacc: 
                gotSac = True
                ref_time = pl.getEYELINK().trackerTime() - startime
    if gotSac:
        Value = [gotSac, sacDist, startLoc, endLoc, ref_time] 
    else:
        Value = [False, None, None, None, None]
    return Value

def check_fix(start_loc, fix_loc, acceptableDev, Dis_for_sacc, scnSize, startime = 0):

    ''' check for eye fixation for a spatial location'''
    
    eye_used = pl.getEYELINK().eyeAvailable()
    fix_loc = centerToTopLeft(fix_loc,scnSize )
    start_loc = centerToTopLeft(start_loc,scnSize )

    fixAcquired = False;fix4Target = False
    if fix_loc:
        fix_loc = [fix_loc[0],fix_loc[1]]
        dt = pl.getEYELINK().getNewestSample() # check for new sample update
        if(dt != None):
            # Gets the gaze position of the latest sample,
            if eye_used == RIGHT_EYE and dt.isRightSample():
                gazePos = dt.getRightEye().getGaze()
            elif eye_used == LEFT_EYE and dt.isLeftSample():
                gazePos = dt.getLeftEye().getGaze()
            gazeDev  = sqrt((gazePos[0]-fix_loc[0])**2+ (gazePos[1]-fix_loc[1])**2)
            gazeStart = sqrt((gazePos[0]-start_loc[0])**2+ (gazePos[1]-start_loc[1])**2)
            if gazeStart > Dis_for_sacc:
                fixAcquired = True
                ref_time = None
            if gazeDev < acceptableDev: 
                fix4Target = True
                ref_time =  pl.getEYELINK().trackerTime() - startime
                
    if fixAcquired or fix4Target:
        gazePos = topLeftToCenter(gazePos,scnSize)
        Value =[fixAcquired, fix4Target, gazePos, gazeDev, ref_time]
    else:
        Value = [False, False, None, None, None, None]
    return Value

# def checkKeyEvent(KEYS_ALLOWED,TERMINATE_UPON_RESP,startime):
    
#     pl.flushGetkeyQueue(); 
#     ev = pygame.event.get()
#     gotKey = False; escapePressed = False
#     for keyp in ev:
#         if (keyp.type == KEYDOWN):
#             keycode = keyp.key
#             if keycode == K_KP_MULTIPLY and (keycode in KEYS_ALLOWED):
#                 pygame.quit(); sys.exit();
#             if (TERMINATE_UPON_RESP == True) and (keycode in KEYS_ALLOWED):
#                 gotKey   = True
#                 respKey  = pygame.key.name(keycode)
#                 respTime = pl.getEYELINK().trackerTime()
#             if keycode == K_ESCAPE: escapePressed = True

#     if gotKey:
#         return [gotKey, escapePressed, respKey, startime, respTime, respTime-startime]
#     else:
#         return [False, False, None, None, None, None]


def offline_mode_start():
     ## force off-line mode first to prevent eyelink freeze
    pl.getEYELINK().setOfflineMode()
    pl.msecDelay(50)

    ## start recording
    error = pl.getEYELINK().startRecording(1,1,1,1)
    if error: return error
    ## wait for 100 ms to prevent data loss
    pl.msecDelay(100); 

    ## send the "SYNCTIME" message to mark the zero time of a trial
    currentTime = pl.getEYELINK().trackerTime()
    pl.getEYELINK().sendMessage("SYNCTIME %d"%currentTime)

# Creates a mock object to be used if tracker doesn't connect for debug purposes
_method_list = [fn_name for fn_name in dir(ConnectedEyeLinker)
                if callable(getattr(ConnectedEyeLinker, fn_name)) and not fn_name.startswith("__")]


def _mock_func(*args, **kwargs):
    pass
   

class MockEyeLinker:
    """Returned if a connection could not be made, useful for debugging away from the trackers."""
    def __init__(self, window, filename, eye, text_color=None):
        self.window = window
        self.edf_filename = filename
        self.edf_open = False
        self.eye = eye
        self.resolution = tuple(window.size)
        self.tracker = None
        self.genv = None
        self.gaze_data = (None, None)
        self.pupil_size = (None, None)
        self.mock = True


        if all(i >= 0.5 for i in self.window.background_color):
            self.text_color = (-1, -1, -1)
        else:
            self.text_color = (1, 1, 1)

        for fn_name in _method_list:
            setattr(self, fn_name, _mock_func)

        # Decorator must return a function
        def record(*args, **kwargs):
            return _mock_func

        self.record = record
