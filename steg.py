#!/usr/bin/env python3

import numpy as np
import sys
import cv2
import hashlib
import argparse
import random
from tqdm import tqdm

# 2-6 for number of bits. 4 is the best for both images
number_of_bits = 4
mask = 0

def generate_mask():
    global mask
    for i in range(number_of_bits):
        mask+= 2**i

def encrypt(channel,value):
    value = value & mask
    return channel ^ value

def decrypt(channel,value):
    value = value & mask
    return channel ^ value

def hide_bits(base,hidden,value):
    hidden = hidden >> (8-number_of_bits)
    hidden = encrypt(hidden,value)
    base = (base >> number_of_bits) << number_of_bits
    final = hidden + base
    return final

def recover_bits(final,value):
    final = final & mask
    final = decrypt(final,value)
    hidden = final << 8-number_of_bits
    return hidden


def image_encode(base_image, hidden_image, height, width, password):

    # Generate password hash for encryption
    hash = hashlib.sha512(str(password).encode("utf-8")).hexdigest()

    # Create empty image for outputting the secret image
    final_image = np.zeros((height, width, 3), np.uint8)
    hash_index  = 0

    for y in tqdm(range(height),ncols=99,desc="Encoding"):
        for x in range(width):

            #Create encryption value from password hash 
            red_key = ord(hash[hash_index])
            green_key = ord(hash[len(hash)-hash_index-1])
            blue_key = ord(hash[abs((len(hash)//2) - hash_index)])
            value = red_key ^ green_key ^ blue_key
            
            # Get image channels
            base_red, base_green, base_blue = base_image[x,y]
            try:
                hidden_red, hidden_green, hidden_blue = hidden_image[x,y]
            except IndexError:
                # If finished encoding image, speed up the process
                final_image[x,y] = (base_red, base_green, base_blue)
                if hash_index == len(hash)-1:
                    hash_index = -1
                hash_index+=1
                continue
            
            # Hide each channel
            final_red = hide_bits(base_red,hidden_red,value)
            final_green = hide_bits(base_green,hidden_green,value)
            final_blue = hide_bits(base_blue,hidden_blue,value)


            # Add pixel to the final image
            final_image[x,y] = (final_red, final_green, final_blue)

            if hash_index == len(hash)-1:
                hash_index = -1
            hash_index+=1
    cv2.imwrite('secret.png', final_image)




def image_decode(secret_image, password):

    # Get shape
    height, width, channels = secret_image.shape

    # Get password hash for decryption
    hash = hashlib.sha512(str(password).encode("utf-8")).hexdigest()
    hash_index = 0

    # Create empty image to form the hidden image
    hidden_image = np.zeros((height, width, 3), np.uint8)

    for y in tqdm(range(height),ncols=99,desc="Decoding"):
        for x in range(width):

            # Generate decryption values
            red_key = ord(hash[hash_index])
            green_key = ord(hash[len(hash)-hash_index-1])
            blue_key = ord(hash[abs((len(hash)//2) - hash_index)])
            value = red_key ^ green_key ^ blue_key

            # Get image channels
            secret_red, secret_green, secret_blue = secret_image[x,y]

            # Recover the bits from each channels
            hidden_red = recover_bits(secret_red,value)
            hidden_green = recover_bits(secret_green,value)
            hidden_blue = recover_bits(secret_blue,value)

            # Put the recovered pixel into a new image
            hidden_image[x,y] = (hidden_red, hidden_green, hidden_blue)

            if hash_index == len(hash)-1:
                hash_index = -1
            hash_index+=1

    cv2.imwrite('hidden.png', hidden_image)


def get_args():
    parser = argparse.ArgumentParser(description="A simple steganography program")
    parser.add_argument("mode", help="Specify whether you want to 'encode' or 'decode'")
    parser.add_argument("password",help="Specify password used for encryption or decryption")
    parser.add_argument("-B","--base",help= "Specify path of the image you want to hide another image in")
    parser.add_argument("-H","--hide", help="Specify path of image you want to hide")
    parser.add_argument("-S","--secret", help="Specify path of the image you want to extract a secret image from")
    parser.add_argument("-b","--bits",default=4,help="Number of bits you want to encrypt with")
    args = parser.parse_args()


    if args.mode != "decode" and args.mode != "encode":
        parser.error("Mode must be specified as 'decode' or 'encode'")

    if args.mode=="encode" and (args.password is None or args.base is None or args.hide is None):
        parser.error("encode mode requires --base, --hide, and --password")

    if args.mode=="decode" and (args.secret is None or args.password is None):
        parser.error("decode mode requires --secret and --password")

    return args


def main():
    args = get_args()

    # Get decode or encode
    option = args.mode

    # Set number of bits to encode/decode with
    global number_of_bits
    number_of_bits = int(args.bits)
    generate_mask()
    
    if option == "encode":
        base_image = args.base
        hidden_image = args.hide
        password = args.password
        base_image = cv2.imread(base_image)
        hidden_image = cv2.imread(hidden_image)

        base_height, base_width, base_channels = base_image.shape
        hidden_height, hidden_width, hidden_channels = hidden_image.shape

        if base_height!=hidden_height and base_width!=hidden_width and base_channels!=hidden_channels:
            print("Sorry but the images need to have the same size and channels")
            sys.exit()
        else:
            image_encode(base_image, hidden_image, base_height, base_width, password)

    elif option == "decode":
        secret_image = args.secret
        password = args.password
        secret_image = cv2.imread(secret_image)
        image_decode(secret_image,password)

    else:
        print('Invalid mode')


if "__main__":

    main()





