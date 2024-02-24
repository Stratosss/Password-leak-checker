import requests
import hashlib
import sys

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
  sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()  #onverts the actual password into SHA1, utf-8 encoding password, then the HASH object into a readable hexadecimal string, and finally the whole string: uppercase
  first5_char, tail = sha1password[:5], sha1password[5:]  #splits the encoded password into 2 groups: up to 5 first digits, from 6th digit till the end of the password
  response = request_api_data(first5_char)        #give only the 5 first chars from the masked-hash password as a safety measure so that it's not recognised
  return get_password_leaks_count(response, tail)  
                                                   
def main(args):  
  for password in args:
    count = pwned_api_check(password)   
    if count:                           
      print(f'{password} was found {count} times... you should probably change your password!')
    else:
      print(f'{password} was NOT found. Carry on!')             
  return 'Password check completed!'

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))    
   

