from flask import Flask, render_template, send_from_directory, request
import requests, os
import urllib
from bs4 import BeautifulSoup

app = Flask(__name__)

media_extensions = ["mp4", "webm", "opus", "mkv", "aac", "m4a", "mp3", "jpg"]

@app.route("/", methods=["GET", "POST"])
def main():
    
    if request.method == "POST":

        for file in os.listdir():
            if file.split(".")[-1] in media_extensions:
                os.remove(file)
            else:
                pass

        link = request.form.getlist("link")[0]
        source = urllib.request.urlopen(f'{link}').read()
        soup = BeautifulSoup(source, features="html.parser")
        title = soup.title.string[:-10]

        if request.form['submit'] == 'Download Video':
            
            os.system(f'youtube-dl -o "%(title)s.%(ext)s" {link}')

            with open("downloaded-files.txt", "a") as f:
                f.write("\n" + title + " Downloaded.") 
           
            for file in os.listdir():
                print(file)
                if file.split(".")[-1] in media_extensions:
                    return send_from_directory(os.getcwd(), file, as_attachment=True)

        elif request.form['submit'] == 'Download Video [iOS]':

            os.system(f'youtube-dl -f mp4 -o "%(title)s.%(ext)s" {link}')

            with open("downloaded-files.txt", "a") as f:
                f.write("\n" + title + " Downloaded.") 
           
            for file in os.listdir():
                print(file)
                if file.split(".")[-1] in media_extensions:
                    return send_from_directory(os.getcwd(), file, as_attachment=True)

        elif request.form['submit'] == 'Download Audio [best quality]':

            os.system(f'youtube-dl -x -o "%(title)s.%(ext)s" {link}')

            with open("downloaded-files.txt", "a") as f:
                f.write("\n" + title + " Downloaded.") 
           
            for file in os.listdir():
                if file.split(".")[-1] in media_extensions:
                    return send_from_directory(os.getcwd(), file, as_attachment=True)

        elif request.form['submit'] == 'Download as an MP3 file':

            os.system(f'youtube-dl -x --audio-format mp3 --audio-quality 0 --embed-thumbnail -o "%(title)s.%(ext)s" {link}')

            with open("downloaded-files.txt", "a") as f:
                f.write("\n" + title + " Downloaded.") 
           
            for file in os.listdir():
                if file.split(".")[-1] in media_extensions:
                    return send_from_directory(os.getcwd(), file, as_attachment=True)
    else:
        return render_template("yt.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)