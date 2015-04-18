import pygtk, gtk, gtk.glade
import gobject
import sys
import os

import locale
import gettext

import v2t_execute
_ = gettext.gettext

if sys.platform=="win32":
	# some win32 distributions have icons set to not display in there theme gtkrc files.
	# The other option if stock icons are not displaying is to do the following:
	#1. open file C:\GTK\share\themes\MS-Windows\gtk-2.0\gtkrc 
	#2. change gtk-button-images = 0 to gtk-button-images = 1 
	gtk.settings_get_default().set_long_property("gtk-button-images", True, "main")


class video2theora(object):
    def __init__(self):
        
        gettext.bindtextdomain("video2theora", "po")
        locale.setlocale(locale.LC_ALL, "")
        gettext.textdomain("video2theora")
        gtk.glade.bindtextdomain("video2theora", "po")
        
        glade_file=os.path.join("data", "v2t.glade")
        self.widgets = gtk.glade.XML(glade_file)
        self.window = self.widgets.get_widget("app_window")
        self.file_chooser_button = self.widgets.get_widget("filechooserbutton")
        self.save_folder_button = self.widgets.get_widget("save_folder_button")
        self.outfile_entry = self.widgets.get_widget("outfile_entry") 
        self.video_quality_slider = self.widgets.get_widget("video_quality_slider")
        self.video_quality_slider.set_tooltip_text(_("10 for best video quality"))
        self.video_quality_label = self.widgets.get_widget("video_quality_label")
        
        self.audio_quality_slider = self.widgets.get_widget("audio_quality_slider")
        self.audio_quality_slider.set_tooltip_text(_("10 for best audio quality"))
        self.audio_quality_label = self.widgets.get_widget("audio_quality_label")
        self.go_button = self.widgets.get_widget("go_button")
        
        self.progress_window = self.widgets.get_widget("progress_window")
        self.progressbar = self.widgets.get_widget("progressbar")
        self.progress_cancel = self.widgets.get_widget("cancel_button")
        
        self.about_dialog = self.widgets.get_widget("aboutdialog1")
        
        self.widgets.signal_autoconnect(self)
        
        
        self.window.connect("delete_event", lambda w,e: gtk.main_quit())
        self.progress_window.connect("delete_event", self.on_cancel_button_clicked)
        
        self.window.show_all()
        
    def on_filechooserbutton_selection_changed(self, widget):
        self.media_file = self.file_chooser_button.get_filename()
        outfile = os.path.basename(self.media_file)
        self.outfile_entry.set_text(outfile[:-3] + "ogv")
        print "media: ", self.media_file
    
    def on_about_clicked(self, widget):
        self.about_dialog.run()
        self.about_dialog.destroy()
    
    def on_quit_clicked(self, widget):
        gtk.main_quit()
    
    def on_convert_clicked(self, widget):
        video_quality = int(self.video_quality_slider.get_value())
        audio_quality = int(self.audio_quality_slider.get_value())
        #print "video: ", video_quality.get_value()
        #print "audio: ", audio_quality.get_value()
        
        backend = "thusnelda" # orig or thusnelda
        handle = v2t_execute.execute(self.media_file, backend, video_quality, audio_quality)
        self.executor = v2t_execute.refresh(handle)
        self.executor.start()
        timer=gobject.timeout_add(1000, self.timer_refresh_callback)
        self.window.hide()
        
        # Set the progress window and bar going
        self.progress_window.show_all()
        self.progressbar.set_pulse_step(0.1) # ten percent
        
    
    # ##############################
    # progress_window callbacks
    
    def on_cancel_button_clicked(self, widget=None, event=None):
        self.progress_window.hide()
        self.executor.set_cancel(True)
        self.executor.set_default()
        self.window.show_all()
        return True # do not destroy the window, we only want to hide it
        
    
    # ##############################
    def timer_refresh_callback(self):
        # set text of progess bar and pulse bar
        self.progressbar.set_text( _("Time Remaining is ") + str(self.executor.get_time_remaining()))
        self.progressbar.pulse()
        
        print "timer_refresh_callback"
        print self.executor.get_program_status()
        if self.executor.get_program_status() == "ended":
            return False # stop the callbacks and display main window again
        #self.progress_bar.set_fraction(percent)
        #self.progress_bar.set_pulse_step(0.1)
        #self.progress_bar.pulse()
        return True
    
    
if __name__ == "__main__":
    gtk.gdk.threads_init()
    app = video2theora()
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
    