# african keyboards 
button_labels = [
   “0”, “1”, “2”, “3”, “4”, “5”, “6”, “7”, “8”, “9”
  “a”, “z”, “e”, “r”, “t”, “y”, “u”, “I”, “o”, “p“
  “s”, “d”, “f”, “g”, “h”, “j”, “k”, “l”, “m”
    w”, “c”, “v”, “b”, “ɓ”,  “ɔ” 
    “capitalize(upload image from path "C:\Users\bideg\Pictures\fleche_jb.jpg")”, “m”, “n”, “ny”, “ŋ”, “backspace(upload image from path "C:\Users\bideg\Pictures\backspace_jb.jpg")”] with each button background color yellow, text font color black"
“?”, “ǃ”, “space”, “,” , “;”, “.”, “Enter (upload image from path "C:\Users\bideg\Pictures\enter_jb.jpg")”] with each button background color yellow, text font color black
# Create a placeholder to store the selected buttons
selected_buttons = []

# Create the keyboard layout
col1, col2, col3, col4, col5, col6 = st.beta_columns(6)

# Iterate over the button labels and create buttons
