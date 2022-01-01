# Important imports
from app import app
from flask import request, render_template, redirect, url_for
import os
from skimage.metrics import structural_similarity
import imutils
import cv2
import numpy as np
from PIL import Image
import textwrap


import requests


## function that gets the random quote
def get_random_quote():
    
	try:
		## making the get request

		response = requests.get("https://quote-garden.herokuapp.com/api/v3/quotes/random?genre=love&count=1")
		if response.status_code == 200:
			## extracting the core data
			json_data = response.json()
			data =json_data['data']

			## getting the quote from the data
			return(data[0]['quoteText'])
		else:
			print("Error while getting quote")
	except:
		print("Something went wrong! Try Again!")



# Adding path to config
app.config['INITIAL_FILE_UPLOADS'] = 'app/static/uploads'

# Route to home page
@app.route("/", methods=["GET", "POST"])
def index():

	# Execute if request is get
	if request.method == "GET":
	    return render_template("index.html")

	# Execute if reuqest is post
	if request.method == "POST":
		option = request.form['options']
		image_upload = request.files['image_upload']
		imagename = image_upload.filename
		card = Image.open(image_upload)
		card = card.resize((300,500))
		card = np.array(card.convert('RGB'))
		
		
		if option == 'add_photo':
			logo_upload = request.files['photo_upload']
			
			pic = Image.open(logo_upload)
			pic= pic.resize((200,300))
			pic = np.array(pic.convert('RGB'))

			card_h, card_w, _ = card.shape
			pic_h , pic_w , _= pic.shape
			center_y = int(card_h / 2)
			center_x = int(card_w / 2)
			top_y = center_y - int(pic_h / 2)
			left_x = center_x - int(pic_w / 2)
			bottom_y = center_y + int(pic_h / 2)
			right_x = center_x + int(pic_w / 2)


			roi = card[top_y: bottom_y, left_x: right_x]
# Add the Logo to the Roi
			result = cv2.addWeighted(roi, 0, pic, 1, 0)
			card[top_y: bottom_y, left_x: right_x] = result



			text = get_random_quote()
			wrapped_text = textwrap.wrap(text, width=20)


			for i in range(len(wrapped_text)):cv2.putText(card, text=wrapped_text[i], org=(0, 10+ i * 20), fontFace=cv2.FONT_HERSHEY_SCRIPT_COMPLEX, fontScale=0.5,color=(255,0,0), thickness=1, lineType=cv2.LINE_4)



			img = Image.fromarray(card, 'RGB')
			
		

			
			img.save(os.path.join(app.config['INITIAL_FILE_UPLOADS'], 'image.png'))
			full_filename =  'static/uploads/image.png'
			return render_template('index.html', full_filename = full_filename)

		

       
# Main function
if __name__ == '__main__':
    app.run(debug=True)
