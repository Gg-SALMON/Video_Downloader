from tkinter import *
from PIL import Image
import requests
from tkinter import filedialog
from pytube import YouTube, Playlist
import customtkinter


# Set Customtkinter appearance and theme
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# Variable
# Thumbnail
global_image = None
# Path where to save video
path = None

def download_completed(stream, file_path):
    """
    Description : refresh labels after completing download : delete "Please wait"
    Parameters:
    Parameters are required because of register-on-complete function, but are not used
    Returns:
    No return
   """
    status2.set(0)
    status2.grid_remove()
    statusp.configure(text="")


def on_download_progress(stream, chunk, bytes_remaining):
    """
    Description : display progress information during download
    Parameters:
    stream (Youtube stream object)
    chunk, bytes_remaining : given by .register_on_progress_callback function in download_yt function
    Returns:
    No return

   """
    bytes_downloaded = stream.filesize - bytes_remaining
    percent = bytes_downloaded / stream.filesize
    status2.grid() # add status2 in the frame
    status2.set(int(percent)) # set value to the progress bar
    window.update()


def download_yt(url, prefixe="YT"):
    """
    Description : Download Youtube video
    Parameters:
    url (str) : valid youtube video url
    prefixe (str) : prefixe for filename for downloaded video
    Returns:
    No return

   """
    button_download.configure(state="disabled") # disabled the download button
    youtube_video = YouTube(url) # create Youtube object from url
    youtube_video.register_on_progress_callback(on_download_progress) # call "on_download_progress" during download progress
    youtube_video.register_on_complete_callback(download_completed) # call "download_completed" once download completed
    stream = youtube_video.streams.get_highest_resolution() # create a stream with the highest resolution available
    status.configure(text="Please wait...") # Change status to "Please wait"
    window.update()
    stream.download(filename_prefix=prefixe, max_retries=10, output_path=path) # Start download"
    status.configure(text="Download completed", text_color=["gray14", "gray84"]) # Change status to "Download completed once completed"
    status2.set(0)  # reset the progress bar"
    status2.grid_remove() #hide the progress bar
    window.update()


def resize_tn(image):
    # Remove black strip from the thumbnail image
    # Return image without black stripes
    colourpixels = image.convert("RGB")
    width, height = colourpixels.size
    colourarray = list(colourpixels.getdata())
    i = 0
    while colourarray[i] == (0, 0, 0):
        i += 1
    j = (len(colourarray) - 1)
    while colourarray[j] == (0, 0, 0):
        j -= 1
    new_image = image.crop((0, i / width, width, height - (height * width - j - 1) / width))
    return new_image


def get_url_info(url):
    """
    Description : get title, size in mb, resolution max and the thumbnail from a Youtube URL (video or playlist)
    Parameters:
    url (str) : valid youtube video url or playlist url
    Returns:
    list with title (str), size_mb (str) , resolution (str) , tn

   """

    url_result, result = check_url(url)
    if url == "Write here a valid url for YouTube video":
        title = size_mb = resolution = tn = ""
    elif url_result == "PlayList":
        t, s, r, tn = get_playlist_info(url)
        title = result+" : "+t
        size_mb = f"Total Size : {r} mb"
        resolution = f"{s} videos in the playlist"

    elif url_result == "YT":
        t, s, r, tn = get_video_info(url)
        title = result+" : "+t
        size_mb = f"Size : {round(s,2)} mb"
        resolution = f"Resolution :{r}"
    else:
        title = check_url(url)[1]
        size_mb = ""
        resolution = ""
        tn = ""
    return title, size_mb, resolution, tn


def get_video_info(url):
    """
    Description : get title, size in mb, resolution max and the thumbnail from a video Youtube URL
    Parameters:
    url (str) : valid youtube video url or playlist url
    Returns:
    list with title (str), size_mb (str) , resolution (str) , tn (str)

   """
    youtube_video = YouTube(url)
    stream = youtube_video.streams.get_highest_resolution()
    title = youtube_video.title
    size_mb = stream.filesize_mb
    resolution = stream.resolution
    tn_url = youtube_video.thumbnail_url
    return title, size_mb, resolution, tn_url


def refresh():
    """
    Description : refresh widgets in the windows
    Parameters:
    None
    Returns:
    None

   """
    # Update status information
    status.configure(text="Please wait...", text_color=["gray14", "gray84"])
    window.config(cursor="watch")
    status2.set(0)
    status2.grid_remove()
    statusp.configure(text="")
    window.update()


    global global_image
    # Update video or playlist information, and thumbnail image
    try:             # Try to get info from url
        t, s, r, tn = get_url_info(input_url.get())
    except Exception as e:      
        if "regex" in f"{e}":   # display error message if url is invalid
            label2.configure(text_color=['red', 'red'], font=("Arial", 55))
            label2.delete("0.0", "end")
            label2.insert("0.0", f"Error - Invalid url", )

        else:                   # display error message if url valid but impossible to access (age restriction, private...)
            label2.configure(text_color=['red', 'red'], font=("Arial", 12))
            label2.delete("0.0", "end")
            label2.insert("0.0", f"Error - {e}", )
        status.configure(text="")
        labelimg.configure(image=YT_image)
        window.update()
        return
    # display information if no error
    label2.configure(text_color=["gray14", "gray84"], font=("Arial", 12))
    label2.delete("0.0", "end")
    label2.insert("0.0", f"{t}\n\n{s}\n{r}",)
    # display thumbnail
    if tn != "":
        global_image = customtkinter.CTkImage(display_thumbnail(tn), size=(160, 120))
        labelimg.configure(image=global_image)
        if "Playlist" in t:
            button_download.configure(command=lambda: download_playlist(input_url.get()))
        else:
            button_download.configure(command=lambda: download_yt(input_url.get()))
    else:
        labelimg.configure(image=YT_image)

    button_download.configure(state="normal" if s else "disabled") #Make download button available if no error

    window.config(cursor="")
    status.configure(text="")


def download_playlist(url):
    """
    Description : download all the video in a playlist Youtube
    Parameters:
    url (str) : valid url for Youtube Playlist
    Returns:
    None

   """
    p = Playlist(url)    # create Playlist object from url
    n = 1                   # create variable to follow download progress
    for video in p.video_urls:    # loop in all the url video in the playlist
        statusp.configure(text=f" Video {n} / {len(p)} from {p.owner}")   # update status  label text to track progress 
        status.configure(text="Please wait...")
        window.update()
        n += 1
        download_yt(video) 


def check_url(url):
    """
    Description : check url format
    Parameters:
    url (str) : url for Youtube Playlist
    Returns:
    n (tuple of str)

   """
    try:
        Playlist(url)
        if "www.youtube.com/playlist?list=" in url:
            n = ("PlayList", "YT Playlist")
        else:
            n = ("YT", "YouTube video")
    except:
        try:
            YouTube(url)
            n = ("YT", "YouTube video")
        except:
            n = ("No_YT", "URL invalid")
    return n


def get_playlist_info(url):
    """
    Description : get playlist information from url of a valid Youtube playlist
    Parameters:
    url (str) : url for Youtube Playlist
    Returns:
    list of value : title (str), num_video (int), total_size (float), tn (str)

    """
 # Refresh progress bar
    status2.set(0)
    status2.grid()
# Create playlist object from url
    p = Playlist(url)
    title = p.title
    num_video = len(p)
    total_size = 0
    status2.set(0)
    status2.grid()
# Loop through all video of the playlist to collect total infos
    for i, video_url in enumerate(p.video_urls):
        youtube_video = YouTube(video_url)
        stream = youtube_video.streams.get_highest_resolution()
        total_size += stream.filesize_mb
        status2.set((i+1)/len(p.video_urls))  # update progress bar to track progress of the info collection
        window.update()
    tn = p.videos[0].thumbnail_url
    status2.grid_remove()
    return title, num_video, round(total_size, 2), tn


def display_thumbnail(tn):
    """
    Description : crete an image from url
    Parameters:
    tn (str) : url for Youtube image
    Returns:
    im (Image object)

    """
    global im
    im = Image.open(requests.get(tn, stream=True).raw)
    im = resize_tn(im)
    return im


def clear_default(event):
    # clear default text in the entry widget
    event.widget.delete(0, 'end')
    event.widget.unbind('<FocusIn>')


def select_directory():
    """
    Description : open dialog box to select a directory and save path in a global variable
    
    """
    global path
    folder_selected = filedialog.askdirectory()
    path = folder_selected


def quit_window():
    # application by destroying the entire window
    window.destroy()


# CREATE WINDOW AND WIDGET

#Create window
window = customtkinter.CTk()

window.title("YOUTUBE DOWNLOADER")
window.iconbitmap("youtube_icon.ico")
window.geometry('750x160')
window.resizable(width=False, height=False)
window.configure(padx=1, pady=1)

# Create frame on the top for URL entry
frame0 = customtkinter.CTkFrame(window,  width=750,)
frame0.pack_propagate(False)
frame0.grid(row=0, column=0, columnspan=4, sticky=EW)

# Create frame on the left for info about url
frame1 = customtkinter.CTkFrame(window, width=430, height=115)
frame1.pack_propagate(False)
frame1.grid(row=1, column=0)

# Create frame in the middle to display thumnbnail(image showing preview of the video)
frame2 = customtkinter.CTkFrame(window, width=170, height=115)
frame2.pack_propagate(False)
frame2.grid(row=1, column=1)

# Create frame on the right for buttons
frame3 = customtkinter.CTkFrame(window,  width=150, height=115)
frame3.pack_propagate(False)
frame3.grid(row=1, column=2)

# Create frame on the bottom for progress bar and status
frame4 = customtkinter.CTkFrame(window,  width=750, height=15)
frame4.grid_propagate(False)
frame4.grid(row=2, column=0, columnspan=3)


# Widget in Frame 0 on the top
      # Entry widget for url
input_url = customtkinter.CTkEntry(frame0, width=750,)
input_url.grid(row=1, column=0, columnspan=4, sticky=EW)
input_url.insert(0, "Write here a valid url for YouTube video")
input_url.bind('<FocusIn>', clear_default)

# Widget in Frame 1 on the left
      # Text box to collect information about url
label2 = customtkinter.CTkTextbox(frame1, width=430, font=("Arial", 12), height=150)
label2.pack(padx=1, pady=2, anchor=W)

# Widgets in Frame 2 in the middle
      # Image to first display in the middle
YT_image = customtkinter.CTkImage(Image.open("YT.png"), size=(160, 120))

      # Label to display the image
labelimg = customtkinter.CTkLabel(frame2, image=YT_image, padx=2, pady=2, text="")
labelimg.place(relx=0.5, rely=0.5, anchor="center")

# Widgets in Frame 3 on the right
      # Define button pady to apply to all button
button_pady = 1
      # Define button to check the url
button_check = customtkinter.CTkButton(frame3, text="Check URL", command=refresh, width=150,)
button_check.pack(padx=1, pady=button_pady)
      # Define button to select the directory where to save video
button_path = customtkinter.CTkButton(frame3, text="Select directory", command=select_directory, width=150,)
button_path.pack(padx=1, pady=button_pady)
      # Define button to start to download video or playlist
button_download = customtkinter.CTkButton(frame3, text="Download", command=refresh, state="disabled", width=150, )
button_download.pack(padx=1, pady=button_pady)
      # Define button to Quit
button_quit = customtkinter.CTkButton(frame3, text="Quit", command=quit_window,  width=150, )
button_quit.pack(padx=1, pady=button_pady)

# Widgets in Frame 4 on the bottom
      # Define status labels to display information during download
status = customtkinter.CTkLabel(frame4, text="",   anchor=W, font=("Arial", 11), height=10, width=150)
status.grid(row=0, column=0, sticky=EW)

statusp = customtkinter.CTkLabel(frame4, text="",   anchor=W, font=("Arial", 11), height=10, width=450)
statusp.grid(row=0, column=1, sticky=EW)

      # Define progress bar to display progress during download
status2 = customtkinter.CTkProgressBar(frame4, height=10, width=150, corner_radius=2, progress_color=("#9CB0EB"))
status2.grid(row=0, column=2, sticky=EW)
status2.set(0)
status2.grid_remove()


window.mainloop()
