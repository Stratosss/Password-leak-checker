import requests
import hashlib
import sys
import flet as ft
from zxcvbn import zxcvbn
from datetime import datetime

def main(page: ft.Page):
  
  # Flet page configuration
  page.theme_mode = ft.ThemeMode.DARK
  page.window.width = 1000
  page.window.height = 400
  # page.window.resizable = False
  
    
  def request_api_data(query_char):              #enters the 5 first chars from password as requested in pwned_api_check()
    url = 'https://api.pwnedpasswords.com/range/' + query_char 
    res = requests.get(url)           #requests a response from the website (URL): returns the tails/suffix of passwords of the prefix (5 first chars) we gave it
    if res.status_code != 200:        
      raise RuntimeError(f'Error fetching: {res.status_code}, check the api and try again')
    return res 

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
    return get_password_leaks_count(response, tail)  
                                                    
  def main(e):
    password = given_password.value
    info_tile.disabled = False
    
    count = pwned_api_check(password)
    
    strength = zxcvbn(given_password.value)
    print(given_password.value)
    score = strength['score']
    score_text.value = f'Password strength score (0-4): {score}'
    feedback = strength['feedback']
    feedback_text.value = f'Feedback: {feedback}'
      
    if count: 
      message_text_found.value = f'Given password was found {count} times... It is recommended to change your password!'
      message_text_found.visible = True                
    else:
      message_text_not_found.value = f'Given password was NOT found!'
      message_text_not_found.visible = True

    # return 'Password check completed!'
  
  
  def on_password_change(e):
    # Hide the old results as soon as they start typing something new
    message_text_found.visible = False
    message_text_not_found.visible = False
    
    # "Lock" the more info tile again
    info_tile.disabled = True
    info_tile.expanded = False # Snap it shut
    
    page.update()


  given_password = ft.TextField(
        label="Insert password to check",
        border=ft.InputBorder.NONE,
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
    else:
        page.theme_mode = ft.ThemeMode.DARK
        theme_button.icon = ft.Icons.LIGHT_MODE
        footer.content.color = ft.Colors.WHITE
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
  message_text_found = ft.Text(color=ft.Colors.RED, weight=ft.FontWeight.BOLD)
  message_text_not_found = ft.Text(color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD)
  score_text = ft.Text(color=ft.Colors.BLUE, weight=ft.FontWeight.BOLD)
  feedback_text = ft.Text(color=ft.Colors.GREY, weight=ft.FontWeight.BOLD)

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
      on_click=main,
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
            title=ft.Text("Click here for more information"),
            affinity=ft.TileAffinity.PLATFORM,
            disabled=True,            
            collapsed_text_color=ft.Colors.RED,
            text_color=ft.Colors.RED,
            controls=[
                ft.ListTile(title=score_text),
                ft.ListTile(title=feedback_text)
            ],
        )
  
  page.add(
    ft.Column(
        controls=[
            header,
            theme_button,
            given_password,
            ft.Row(
            controls=[calculation_button]),
            message_text_found,
            message_text_not_found,
            info_tile,
            footer
        ],
        spacing=10
    ),
      
 )
          
if __name__ == "__main__":
    ft.app(main) 
  

