#!/bin/env python

# Copyright (C) 2008  Peter Gill - peter@majorsilence.com
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import time
import subprocess
import select
import re
import threading
if sys.platform=='win32':
    import win32api
    import win32process
    import win32con



import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

def convert_time(v_time=None):
    if time==None: 
        return None
    current_time = int(time.time())
    v_time = current_time - v_time # time difference
    print v_time
    hours = 0 
    minutes = 0 
    seconds = 0 
    time_string = "" 

    if v_time >= 3600:
        hours = v_time / 3600
        v_time = v_time - (hours * 3600)
    if v_time >= 60:
        minutes = v_time / 60
        v_time = v_time - (minutes * 60)
    #remaining time is seconds 
    seconds = v_time
    time_string = time_string + str(hours).zfill(2) + ":" + str(minutes).zfill(2) + ":" + str(seconds).zfill(2)
    #return time in Hours:Minutes:Seconds format 
    print time_string
    return time_string


def cancel_prog(handle=None):
    if handle is not None:
        if sys.platform=='win32':
            try:
                win32api.TerminateProcess(int(handle._handle), -1)
            except Exception , err:
                print "Error: ", err
        else:
            os.kill(handle.pid,signal.SIGKILL)
    return

def get_file_type(file_name):
    return os.path.splitext(file_name)[1][1:]
    
def check_exists(file_name=None):
    if file_name is None:
        return False
        
    return_value = 0 # 0 means no iso file with the same name present, or if present overwrite
    output_file = os.path.splitext(file_name)[0] + ".ogv"
    print iso_file
    if os.path.isfile(iso_file):
        msg = _("File \"%s\" alreay exists.  Do you wish to overwrite.") % os.path.basename(output_file)
        dialog=gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO, msg)
        response = dialog.run()
        print response
        if response==gtk.RESPONSE_YES:
            os.remove(output_file)
        else:
            return_value=1
        dialog.destroy()
    return return_value

def execute(filename=None, backend=None, video_quality=None, audio_quality=None):
    #out_file = os.path.splitext(filename)[0] + ".ogv"
    #print out_file
    app=None
    
    if (backend == "orig"):
        app="ffmpeg2theora-0.22.exe"
    elif (backend == "thusnelda"):
        app="ffmpeg2theora-0.22-thusnelda.exe"
    
    if video_quality!=None:
        v_quality = "-v %s" % video_quality # -v or -videoquality
    else:
        v_quality = "-v 5" # 5 is default, can be 1 to 10, 10 being the best
        
    if audio_quality != None:
        a_quality = "-a %s" % audio_quality # -a or -audioquality
    else:
        a_quality = "-a 3" # 1 is default, can be -2 to 10

    
    path_list=os.environ["PATH"].split(":")
    path_list.append(os.getcwd())
    for x in path_list:
        launch = os.path.join(x, app)
        print app
        try:
            if sys.platform=='win32':
                handle=V2TPopen([launch, filename, v_quality, a_quality],shell=False, bufsize=32400, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=win32process.CREATE_NO_WINDOW, read=10)
            else:
                handle = subprocess.Popen([launch, filename, v_quality, a_quality], shell=False, bufsize=32400, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            print "Error launching program.  Program not found in path."
        else:
            print "Program launched:", app, filename
            return handle
    return None # No program running

class refresh(threading.Thread):
    percent = 0.0
    time_remaining="??:??:??"
    is_running = False
    def __init__(self, handle=None):
        threading.Thread.__init__(self)
        if handle==None:
            # class is only being used to aquire information from the class object percent
            refresh.is_running = False
        else:
            refresh.is_running = True
        self.handle=handle
        self.cancel = False
    
    def set_default(self):
        refresh.percent = 0.0
        refresh.time_remainining = "??:??:??"
        refresh.is_running = False
    
    def set_cancel(self, cancel=False):
        self.cancel=cancel
    
    def get_percent(self):
        #time.sleep(0.01) # keep python from killing the cpu
        return refresh.percent
        
    def get_time_remaining(self):
        return refresh.time_remaining
        
    def get_program_status(self):
        if refresh.is_running == False:
            return "ended"
        return "running"
        
    def read_progress(self, sout):
        #pattern = re.compile('\[\d*%\]') # brackets followed by digit, followed by any number of characters, fowllowed by percent sign and closing bracket
        try:
            #per= int(pattern.findall(sout)[0][1:-2]) # find [Num%] and remove both[] and %, leave only the number
            
            # for whatever reason the time running does not seem to work correctly.  As if time slows down, so use own time running from within python
            #pos = sout.rfind("audio:")
            #time_running = sout[pos-9:pos].strip()
            #if time_running.strip() != "":
            #    print "Time Running: ", time_running
            
            pos = sout.rfind("time remaining:")
            time_remaining = sout[pos+15:pos+15+9].strip() # 14 (len("time remaining")) + 9 (length of the time)
            if time_remaining.strip() != "" and len(time_remaining) == 8:
                refresh.time_remaining = time_remaining
                print "Time Remaining: ", time_remaining
            #refresh.percent = per/100.0
            #print percent
        except:
            pass
            #print "No percent found"
            #print sout
        #time.sleep(0.1)
    
    def run(self):
        while self.handle.poll()==None:
            read_output=""
            if sys.platform=="win32":
                sout = self.handle.recv_some()
            else:
                sout, sin, serr = select.select([self.handle.stdout], [], [self.handle.stderr], 0)
            #print "length: ", len(sout)
            if self.cancel:
                cancel_prog(self.handle)
            for line in sout:
                if sys.platform=="win32":
                    read_output += line
                    print "line: ", line
                    #break # On windows 
                else:
                     read_output += line.readline(80)
            self.read_progress(read_output)
            #print "percent-%s: -count: %s" % (file_info[0], self.percent)   
        refresh.is_running = False
        return
            
class V2TPopen(subprocess.Popen):
    """
    Threaded subclass of subprocess. Popen to allow for non-blocking input output of subprocesses.

    Returns a list of lists.
    eg. return [ [stdout, buffer], [stderr, buffer] ]
    Usage:
    out, err = MyPopen.recv_some()
    for x in out:
        print "This is the output: " x
    """
    #TODO: Add exception handling
    
    class PipeThread(threading.Thread):
        def __init__(self, fin, chars=80):
            threading.Thread.__init__(self)
            self.chars=chars
            self.fin = fin
            self.sout = []
            #self.sout = ""
            
        def run(self):
            while True:
                #temp = self.fin.readline()
                temp=self.fin.read(self.chars)
                if not temp: break
                self.sout.append(temp)
                #self.sout += temp

        def get_output(self):
            return self.sout
                
        def reset(self):
            self.sout = []
            #self.sout = ""
        
    def __init__(self, args=None, bufsize=0, executable=None, stdin=None, stdout=None, stderr=None, preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None, universal_newlines=False, startupinfo=None, creationflags=0, threaded=True, read=80):
        subprocess.Popen.__init__(self,args=args, bufsize=bufsize, executable=executable, stdin=stdin, stdout=stdout, stderr=stderr, preexec_fn=preexec_fn, close_fds=close_fds, shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines, startupinfo=startupinfo, creationflags=creationflags)
        if not threaded:
            pass
        else:
            self.out_pipe, self.err_pipe = self.PipeThread(self.stdout, read), self.PipeThread(self.stderr)
            self.out_pipe.start(), self.err_pipe.start()
    
    def recv_some(self):
        """
        Returns a copy of the lists holding stdout and stderr
        Before returning it clears the original lists
        """

        # 0.1 seems to jam up the program.  No sleep seems to cause mencoder to just flounder.
        # Sleep 0.01 seems to work very well, keeping mencoder busy, and program smooth.
        time.sleep(0.01)
        out, err = self.out_pipe.get_output(), self.err_pipe.get_output()
        self.out_pipe.reset()
        self.err_pipe.reset()
        out.extend(err) # this will sort of get it to work with dvdauthor and mkisofs
            # for some reason only output to read is from the stderr for those programs
        return out #[out, err]
    
    def set_priority(self, pid=None, priority=0):
        """
        Set the Priority of a Windows Process.  Priority is a value between 0-5 where
        2 is normal priority.  Defaults to lowest Priority.
        """
        priority_classes=[win32process.IDLE_PRIORITY_CLASS,
                          win32process.BELOW_NORMAL_PRIORITY_CLASS,
                          win32process.NORMAL_PRIORITY_CLASS,
                          win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                          win32process.HIGH_PRIORITY_CLASS,
                          win32process.REALTIME_PRIORITY_CLASS]
        if pid == None:
            pid=self.pid
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(handle, priority_classes[priority])
            
if __name__ == "__main__":
    start = int(time.time())
    time.sleep(65)
    convert_time(start)