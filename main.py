import requests
import hashlib
import flet as ft
from zxcvbn import zxcvbn
from datetime import datetime


def main(page: ft.Page):
  #creating text objects for the results of the password check, and the strength score and feedback from zxcvbn library
  message_text = ft.Text(color=ft.Colors.RED, weight=ft.FontWeight.NORMAL)
  # message_text_not_found = ft.Text(color=ft.Colors.GREEN, weight=ft.FontWeight.NORMAL)
  score_text = ft.Text(weight=ft.FontWeight.NORMAL)
  feedback_text = ft.Text(color=ft.Colors.WHITE, weight=ft.FontWeight.NORMAL)
  strength_bar = ft.ProgressBar(width=200, height=8, border_radius=5, value=0)
  
  colour_coding={
    0: ft.Colors.RED,
    1: ft.Colors.AMBER,
    2: ft.Colors.ORANGE,
    3: ft.Colors.TEAL,
    4: ft.Colors.GREEN
  }
  
  # Flet page configuration
  page.theme_mode = ft.ThemeMode.DARK
  page.window.width = 1000
  page.window.height = 620
  page.window.min_width = 600   # Prevents the UI from "crushing"
  page.window.min_height = 400
  page.window.resizable = True # Prevent resizing to maintain layout integrity
  page.title = "Password Leak Checker App"
    
  def request_api_data(query_char):              #enters the 5 first chars from password as requested in pwned_api_check()
    try: 
      url = 'https://api.pwnedpasswords.com/range/' + query_char 
      res = requests.get(url, timeout=5) # Added a timeout so it doesn't hang forever
      res.raise_for_status() # This triggers an error if the site is down (e.g., 500 error)
      return res
    except requests.exceptions.HTTPError: # This catches HTTP errors, such as 404 (not found) or 500 (server error)
        return "API ERROR (Server Issue)"  
    except requests.exceptions.ConnectionError: # This catches connection errors, such as when the user is offline or the server is unreachable
        return "CONNECTION ERROR (Check your internet connection)"
    except requests.exceptions.Timeout: # This catches timeout errors, which occur when the server takes too long to respond
        return "TIMEOUT ERROR (Server is taking too long to respond)"
      
  def get_password_leaks_count(hashes, hash_to_check):  #Enters function with hashes= response from website, and hash_to_check= tail from password
    hashes = (line.split(':') for line in hashes.text.splitlines()) #Creates tuples with line.split(:) command to make the resposes of the website each one of them a tupple (Encoded Password : counts it was found)
    for h, count in hashes:   
      if h == hash_to_check:   #It checks in the hashes list if any of them match the rest of my password(), if it finds, it returns the counts of it.
        return count
    return 0   

  def pwned_api_check(password):
    sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()  #converts the actual password into SHA1, utf-8 encoding password, then the HASH object into a readable hexadecimal string, and finally the whole string: uppercase
    first5_char, tail = sha1password[:5], sha1password[5:]  #splits the encoded password into 2 groups: up to 5 first digits, from 6th digit till the end of the password
    response = request_api_data(first5_char)        #give only the 5 first chars from the masked-hash password as a safety measure so that it's not recognised
    if isinstance(response, str):
        return response
    return get_password_leaks_count(response, tail)  
  
  def validation_for_password(e): # This function is used to validate the password input before calling the API check, it ensures that the user has entered a password and provides feedback if they haven't.
    password = given_password.value
    if not password or password.isspace():  # Check if the password is empty or only contains whitespace
      given_password.value=''  # Clear the input field
      message_text.value = 'Please enter a password to check (cannot be empty or only spaces).'
      message_text.visible = True
      page.update()
      return False
    return input_func(password)
                                                    
  def input_func(password):
      count = pwned_api_check(password)
      if count in ["API ERROR (Server Issue)", "CONNECTION ERROR (Check your internet connection)", "TIMEOUT ERROR (Server is taking too long to respond)"]:
        message_text.value = f"⚠️ {count}.\n      Please try again later."
        message_text.color = ft.Colors.RED
        message_text.visible = True
        info_tile.visible = False
        page.update()
        return
      else:
        info_tile.visible = True
        strength = zxcvbn(password)
        score = strength['score']
        score_text.value = f'Password strength score (0-4): {score}'
        feedback_warning = '\nWarnings:\n- ' + strength['feedback']['warning'] if strength['feedback']['warning'] else '\nNo warnings!! 🥳'
        feedback_suggestions = '\nRecommendations:\n- ' + '\n- '.join(strength['feedback']['suggestions']) if strength['feedback']['suggestions'] else ''
        feedback_text.value = f'{feedback_warning}\n{feedback_suggestions}'
          
        if count:
          message_text.value = f'⚠️ Given password was found {count} times... It is recommended to change your password!'
          message_text.visible = True                
        else:
          message_text.value = f'Given password was NOT found!'
          message_text.visible = True
          message_text.color = ft.Colors.GREEN
        
        score_text.color= colour_coding.get(score, ft.Colors.WHITE) # Default to WHITE if score is out of range 
        strength_bar.value = score  / 4  # Normalize score to range [0, 1]
        strength_bar.color = colour_coding.get(score, ft.Colors.GREY)
        strength_bar.animate_width = 300  
        page.update()
        return
  
  def on_password_change(e):
    # Hide the old results as soon as they start typing something new
    message_text.visible = False
    info_tile.expanded = False # Snap the tile shut
    info_tile.visible = False # Hide the tile completely until they check the new password
    message_text.color = ft.Colors.RED # Reset color to default for new password
    page.update()


  given_password = ft.TextField(
        label="Insert password to check",
        border=ft.InputBorder.NONE,
        border_radius=10,
        password=True,
        can_reveal_password=True,
        filled=True,
        on_change=on_password_change
  )
  
  # Theme change function
  def change_theme(e):
    if page.theme_mode == ft.ThemeMode.DARK:
        page.theme_mode = ft.ThemeMode.LIGHT
        theme_button.icon = ft.Icons.DARK_MODE
        footer.content.color = ft.Colors.BLACK
        info_tile.title.color = ft.Colors.BLACK
        feedback_text.color = ft.Colors.BLACK
    else:
        page.theme_mode = ft.ThemeMode.DARK
        theme_button.icon = ft.Icons.LIGHT_MODE
        footer.content.color = ft.Colors.WHITE
        info_tile.title.color = ft.Colors.WHITE
        feedback_text.color = ft.Colors.WHITE
    page.update()
  
  def handle_tile_change(e: ft.Event[ft.ExpansionTile]):
        page.show_dialog(
            ft.SnackBar(
                duration=1000,
                content=ft.Text(
                    value=(
                        f"ExpansionTile was "
                        f"{'expanded' if e.data == 'true' else 'collapsed'}"
                    )
                ),
            )
        )
        if e.control.trailing:
            e.control.trailing.icon = (
                ft.Icons.ARROW_DROP_DOWN
                if e.control.trailing.icon == ft.Icons.ARROW_DROP_DOWN_CIRCLE
                else ft.Icons.ARROW_DROP_DOWN_CIRCLE
            )
            page.update()
                  
  #App Contents & Design      
  header = ft.Text(
      "Password Leak Checker!",
      size=40,
      weight=ft.FontWeight.BOLD,
      color=ft.Colors.BLUE_700
      )

  theme_button = ft.FilledButton(
    content ="",
    on_click=change_theme,
    disabled=False,
    icon=ft.Icons.LIGHT_MODE
    )
  
  calculation_button = ft.FilledButton(
      content="Check Password", 
      on_click=validation_for_password,
      icon=ft.Icons.SEARCH
      )
  
   
  footer = ft.Container(
    content=ft.Text(
        f"Developed by Stratos Gialouris - All rights reserved © {datetime.now().year}",
        size=16,
        color=ft.Colors.WHITE,
        italic=True,
    ),
    alignment=ft.Alignment.BOTTOM_RIGHT
  )

  info_tile=ft.ExpansionTile(
            expanded=False,
            title=ft.Text("Password Strength Analysis",weight=ft.FontWeight.BOLD),
            affinity=ft.TileAffinity.PLATFORM,
            visible=False,            
            collapsed_text_color=ft.Colors.WHITE,
            text_color=ft.Colors.WHITE,
            controls=[
                ft.ListTile(title=ft.Row(
                  controls =[
                    score_text,
                    strength_bar
                  ])),
                ft.ListTile(title=ft.Text('Feedback',weight=ft.FontWeight.BOLD),
                            subtitle=feedback_text
                )
            ],
        )
  
  page.add(
    ft.Column(
        controls=[
            header,
            theme_button,
            given_password,
            calculation_button,
            message_text,
            info_tile,
        ],
        spacing=10
    ),
    ft.Container(expand=True), # This container will take up all the remaining space, pushing the footer to the bottom when the message text and info tile are not visible
    footer
  )
 
if __name__ == "__main__":
    ft.app(main) 
  

