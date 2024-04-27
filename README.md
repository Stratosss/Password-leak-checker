# Password Leak Checker
## Overview
 - This project offers a thorough search for leaks for any given password, utilizing the potential of an online password checker API from https://haveibeenpwned.com/Passwords
 - It further utilises an SHA-1 encryption, and doesn't expose the password fully online. Instead, it checks for potential matches for the first 5 characters, and when the results are downloaded it checks for a match for the rest of the password.
