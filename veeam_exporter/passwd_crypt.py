#!/usr/bin/python3.9
# -*- coding:utf-8 -*-
#************************************************************************

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64, getpass
import sys, argparse

#******************************************************************************************
class myArgs:
  attrs = [ 'key', 'password', 'decrypt'
          ]
  def __init__(self):

    for attr in myArgs.attrs:
        setattr(self, attr, None)

#******************************************************************************************
def encrypt(key, plaintext):
    cipher = AES.new(key, AES.MODE_GCM)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
    return ciphertext, nonce, tag

#***********************************************
def decrypt(key: str, ciphertext) -> str:
   if isinstance(ciphertext, str):
        ciphertext = base64Decoding( ciphertext )
   if len(ciphertext) < 16 :
      raise "invalid ciphertext length: too short"
   nonce = ciphertext[0:16]
   tag = ciphertext[-16:]
   ciphertext = ciphertext[16:-16]

   cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
   plaintext = cipher.decrypt(ciphertext)
   if tag is not None:
      try:
            cipher.verify(tag)
      except ValueError as exp:
            plaintext = None
            raise str(exp)

   return plaintext

#******************************************************************************************
def base64Encoding(input):
  dataBase64 = base64.b64encode(input)
  dataBase64P = dataBase64.decode("UTF-8")
  return dataBase64P

#******************************************************************************************
def base64Decoding(input):
   return base64.decodebytes(input.encode("ascii"))

#******************************************************************************************
def main():

   # get command line arguments

   parser = argparse.ArgumentParser(description='generate encrypted password with shared key.')

   parser.add_argument('-d ', '--decrypt'
                        , action='store_true'
                        , help='decrypt the provided text.')

   parser.add_argument('-k', '--key'
                        , help='set the key to encrypted set password.'
   )

   parser.add_argument('-p ', '--password'
                        , help='password to crypt.'
   )


   inArgs = myArgs()
   args = parser.parse_args(namespace=inArgs)

   key = getpass.getpass("shared key: ")
   if key is None or key == "":
      key = get_random_bytes(16)
      print("rand key: {0} ".format( base64Encoding( key ) ) )
   else:
      # convert to array of byte
      key = key.encode("utf-8")

   action = "encrypt"
   if args.decrypt:
      action = "decrypt"
   plaintext = getpass.getpass("password to {}: ".format(action))
   # plaintext = None
   if plaintext is None or plaintext == "":
      plaintext = "text to {}".format(action)

   if action == "encrypt":
      ciphertext, nonce, tag = encrypt(key, plaintext)
      fullciphertext = base64Encoding( nonce + ciphertext + tag)
      print("encrypted result: {0} ".format(fullciphertext))
   else:
      try:
         plaintext = decrypt(key, plaintext)
         print("content: {}".format(plaintext))
      except ValueError:
         print("Key incorrect or message corrupted")    
         plaintext = None

   sys.exit(0)

# end main...

#*****************************************************************************
if __name__  == '__main__':
   main()

