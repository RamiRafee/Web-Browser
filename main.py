import sys
from url import URL
from utils import lex
import tkinter
WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100
def layout(text, WIDTH, HEIGHT,emoji_mapping = {}):
    """
    Arrange the text into a list of positions and characters,
    handling newline characters to create paragraph breaks.
    
    Args:
        text (str): The text to layout.
    
    Returns:
        list: A list of tuples (x, y, character) representing 
              each character's position.
    """
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP + 50

    cursor_x, cursor_y = HSTEP, VSTEP
    buffer = ""
    in_code = False

    for c in text:
        if c == ":":
            if in_code:
                # Process code
                code = buffer

                buffer = ""
                in_code = False
                if code in emoji_mapping:
                    cursor_x+= 31
                    display_list.append((cursor_x, cursor_y, emoji_mapping[code]))
                    cursor_x += 31  # Adjust for emoji size
                # else:
                #     display_list.append((cursor_x, cursor_y, ":" + code + ":"))
                #     cursor_x += HSTEP
            else:
                in_code = True
        elif in_code:
            buffer += c

        elif c == '\n':
            cursor_y += VSTEP * 2  # Increment by more than VSTEP for paragraph breaks
            cursor_x = HSTEP
        elif c in emoji_mapping:
            display_list.append((cursor_x, cursor_y, emoji_mapping[c]))
            cursor_x += 16  # Adjust for emoji size
        else:
            display_list.append((cursor_x, cursor_y, c))
            cursor_x += HSTEP
            if cursor_x >= WIDTH - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP
    
    return display_list
class Browser:
    def __init__(self):
        
        
        
        self.window = tkinter.Tk()
        self.window.title("Creator Browser")
        
        self.url_frame = tkinter.Frame(self.window)
        self.url_frame.pack(side=tkinter.TOP, fill=tkinter.X)
        
        self.title_label = tkinter.Label(self.url_frame, text="Page Title")
        self.title_label.pack(side=tkinter.TOP, fill=tkinter.X)
        
        self.url_entry = tkinter.Entry(self.url_frame)
        self.url_entry.bind("<Return>", self.load_url)
        self.url_entry.pack(side=tkinter.TOP, fill=tkinter.X)
        
        self.canvas_frame = tkinter.Frame(self.window)
        self.canvas_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)



        


        self.canvas = tkinter.Canvas(
            self.canvas_frame, 
            width=WIDTH - 20,  # Adjusted for scrollbar width
            height=HEIGHT - 100,  # Adjusted for title and URL bar
            bg='white'
        )
        self.canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.window.bind("<Configure>", self.on_resize)
        self.scrollbar_rect = None
        self.max_scroll = 0
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.on_mousewheel)
        self.window.bind("<Button-4>", self.on_mousewheel_linux)
        self.window.bind("<Button-5>", self.on_mousewheel_linux)
        self.window.iconbitmap("Assets\window_icon.ico")
        # self.load_emoji_images()
        self.emoji_mapping = self.create_emoji_mapping()
    def scroll_canvas(self, *args):
        self.canvas.yview(*args)
        self.scroll = int(self.canvas.canvasy(0))
    def scrolldown(self, e=None):
        self.scroll = min(self.scroll + SCROLL_STEP, self.max_scroll)
        self.update_scroll()

    def scrollup(self, e=None):
        self.scroll = max(0, self.scroll - SCROLL_STEP)
        self.update_scroll()
    def update_scroll(self):
        # Calculate maximum scroll based on the height of the document
        try:
            self.max_scroll = max(1, max(y for _, y, _ in self.display_list) - self.canvas.winfo_height())
        except ValueError:
            self.max_scroll = 1
        # Ensure we do not scroll past the last entry
        self.scroll = min(self.scroll, self.max_scroll)
        self.canvas.yview_moveto(self.scroll / self.max_scroll)
        self.draw()
    def on_mousewheel(self, event):
        if event.delta < 0:
            self.scrolldown(event)
        else:
            self.scrollup(event)

    def on_mousewheel_linux(self, event):
        if event.num == 4:
            self.scrollup()
        elif event.num == 5:
            self.scrolldown()
    def on_resize(self, event):
        """
        Handle the window resize event by adjusting the layout
        of the content to fit the new window size.
        
        Args:
            event: The event object containing the new width and height.
        """
        # self.canvas.config(width=event.width - 20, height=event.height - 100)
        self.display_list = layout(self.text, event.width - 20, event.height - 100 , self.emoji_mapping)
        # try:
        #     self.max_scroll = max(0, max(y for _, y, _ in self.display_list) - self.canvas.winfo_height())
        # except ValueError:
        #     self.max_scroll = 1
        self.update_scroll()
    def draw(self):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        for x, y, c in self.display_list:
            if y > self.scroll + self.window.winfo_height(): continue
            if y + VSTEP < self.scroll: continue
            # self.canvas.create_text(x, y - self.scroll, text=c)
            if isinstance(c, str):
                self.canvas.create_text(x, y - self.scroll, text=c)
            else:
                self.canvas.create_image(x, y - self.scroll, image=c)
        # Draw the scrollbar
        if self.max_scroll > canvas_height:
            scrollbar_height = (canvas_height / self.max_scroll) * canvas_height
            scrollbar_y = (self.scroll / self.max_scroll) * (canvas_height - scrollbar_height)
            
            if self.scrollbar_rect:
                self.canvas.delete(self.scrollbar_rect)
            
            self.scrollbar_rect = self.canvas.create_rectangle(
                canvas_width - 10, scrollbar_y,
                canvas_width, scrollbar_y + scrollbar_height,
                fill="blue", outline="blue"
                )
    def load_url(self, event=None):
        url = self.url_entry.get()
        self.load(URL(url))
    def load(self,url):
        """
        Load the content from the given URL and display it.
        
        Args:
            url (URL): The URL object to load content from.
        """
        try:
            self.url_entry.delete(0, tkinter.END)
            self.url_entry.insert(0, url.scheme +"://" + url.host +  url.path)
            self.body = url.request()
            if url.view_source:
                print(self.body)  # Print the raw HTML source
            else:
                self.text = lex(self.body)
            
            self.display_list = layout(self.text, self.window.winfo_width(), self.window.winfo_height(), self.emoji_mapping)
            
        except Exception as e:
            # Log the exception (optional)
            print(f"Error loading URL: {e}")
            # Fallback to about:blank
            self.url_entry.insert(0, "about:blank")
            self.text = ""
            self.display_list = layout(self.text, self.canvas.winfo_width(), self.canvas.winfo_height(), self.emoji_mapping) 
        self.update_scroll()       
    def load_emoji_images(self):
        """
        Load all emoji images from the 'emojis' directory into a dictionary.
        """
        self.emoji_images = {}
        import os
        emoji_dir = "Assets/emojis"
        for file in os.listdir(emoji_dir):
            if file.endswith(".png"):
                name = os.path.splitext(file)[0]
                self.emoji_images[name] = tkinter.PhotoImage(file=os.path.join(emoji_dir, file))
    def create_emoji_mapping(self):
        """
        Create a mapping of emoji characters to their corresponding image filenames.
        """
        # Example mapping; update with actual file names
        return {
            "1F600": tkinter.PhotoImage(file="Assets/emojis/1F600.png"),
            # other emojis as needed
        }
if __name__ == "__main__":
    if len(sys.argv) > 1:
        Browser().load(URL(sys.argv[1]))
        tkinter.mainloop()
    else:
        # Default file path for quick testing

        Browser().load(URL(""))
        tkinter.mainloop()
