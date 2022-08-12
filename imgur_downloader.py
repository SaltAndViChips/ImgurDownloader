#!/usr/bin/env python
import argparse, os, sys, yaml
import urllib.request
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
import glob

def parse_args():
    parser = argparse.ArgumentParser(description='Download an Imgur album/gallery into a folder.')
    parser.add_argument('-c', '--config', type=argparse.FileType('r'), default=os.path.expanduser(r'config.yaml'),
            help='config file to load settings from')
    parser.add_argument('-a', '--album', help='album ID to download from Imgur (can be specified multiple times)', required=True, action='append')
    parser.add_argument('-d', '--directory', default=fr"images", help='directory to save images into')

    return parser.parse_args()

def load_config(config_file):
    print('Loading config file {}'.format(config_file.name))
    try:
        config = yaml.load(config_file, yaml.BaseLoader)
    except yaml.YAMLError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Error loading YAML {} on line {}'.format(e, exc_tb.tb_lineno))

    return config

def download_image(image_url, download_path, filename):
    """
    Download image and save it to file path
    """
    try:
        urllib.request.urlretrieve(image_url, download_path)
        print(f"File {image_url} downloaded as {filename}")

    except urllib.error.URLError as e:
        print("Error downloading image '{}': {}".format(image_url, e))
    except urllib.error.HTTPError as e:
        print("HTTP Error download image '{}': {!s}".format(image_url, e))

def main():
    global config
    global args

    args   = parse_args()
    config = load_config(args.config)

    # Initialise Imgur client
    client = ImgurClient(config['imgur_client_id'], config['imgur_client_secret'])

    if glob.glob(fr"images\*.jpg"):
        print("\nClearing Cache...\n")
        for path in glob.glob(fr"images\*.jpg"):
            print(f"Deleting {path}")
            os.remove(path)
    else:
        print("\nCache Empty")

    choice = input("\n1. args\n2. list\n\n")

    if choice == "2":
        with open('links.txt') as f:
            savedalbums = [line.rstrip() for line in f]

        args.album = []
        for album in savedalbums:
            args.album.append(album.replace("https://imgur.com/a/", ""))


    for album in args.album:
        # Get our album images
        try:
            images = client.get_album_images(album)
            imagename = client.get_album(album).description.split("\n")[0].replace(" ", "_").replace("\"","")
            # debug = client.get_album(album)
        except ImgurClientError as e:
            print('ERROR: {}'.format(e.error_message))
            print('Status code {}'.format(e.status_code))

        print("Downloading album {} ({!s} images)".format(album, len(images)))

        # Download each image
        for image in images:
            # Turn our link HTTPs
            link      = image.link.replace("http://","https://")
            # Get our file name that we'll save to disk
            download_path = os.path.join(args.directory, imagename+".jpg")
            if os.path.isfile(download_path):
                x=1
                while os.path.isfile(download_path):
                    print(f"\nFile exists for image {imagename}, renaming to {imagename}_{x})")
                    download_path = os.path.join(args.directory, f"{imagename}_{x}.jpg")
                    x+=1
                download_image(link, download_path, imagename)
            else:
                download_image(link, download_path, imagename)

    from grid import create_grid
    choice = input("\nPrint Grid?\n1. Yes\n2. No\n\n")
    if choice == "1":
        create_grid()


if __name__ == '__main__':
    main()
