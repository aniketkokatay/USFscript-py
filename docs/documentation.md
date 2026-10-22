To Make a screen
import usf
s1=usf.screen(sc_id,icon,orientation,colours)
sc_id-> The Name of the Screen; String
icon-> The icon of the screen; tuple; (length,width,icon as a list of 1s and 0s)
orientation-> default "l" {landscape}, or a string of the form "lengthxbreadth", or a tuple (length,breadth) {both integers}
colours-> Main colour scheme for all the buttons, text and displays; tuple {button/icon primary, button secondary+button text colour,screen bg colour} #in hex code

1. BUTTONs
s1.add_button(length,width,icon,action,colours,label,font,exp)
length,width,icons; integer, integer, list
action; what should the button do on click
colours; tuple (button primary, text+button secondary); will default to the one given in the screen if not entered
label-> text associated with the button; string {currently only supports alphabets, digits and spaces}
font; Size of the text
exp; expression to multiply to the button exp; string formatted according to latex
Button action function; s1.switch(sc_id) , will create an action to switch to the entered sc_id on button click

2. BACK
s1.back(sc_id) ; creates a back button icon at the top left of the screen which allows you to go back to your past screen

3. Keyboard;
s1.keyboard(type,display,max_len,target,on_enter)
type-> "a"(alphabets),"d"(digits),"ad"(alphanumeric keyboard) {currently only "d" is supported}
max_len-> maximum value of the entered number {cannot be greater than 15 for now}
target-> target variable where the entered number will be stored, string like "test" or latex formatted "t_{{est}}"
on_enter-> action that should occur when enter key is pressed

4. Expression
s1.add_exp(exp,colour,action,trans_line,trans_bg)
exp-> latex formatted string
colour-> colour of the graph {if applicable}
action-> action on click {if applicable}
trans_line, trans_bg-> transparency of the border and interior respectively {if applicable}

5. Image
s1.add_image(length,width,icon,action,colours,coords,exp,fill)
length,width,icons; integer, integer, list
action; what should the button do on click
colours; tuple (button primary, text+button secondary); will default to the one given in the screen if not entered
coords-> coordinates of the image (x,y)
exp; expression to multiply to the button exp; string formatted according to latex
fill-> 0 {the 1s in the list will be coloured},1 {the zeros in the list will be coloured}, 2 {1s will be coloured the secondary colour and 0s with the primary colour}
in the first two cases the main colour will be the secondary colour

6. Label
s1.add_label(label,font,action,label_maxlen,coords,colour)
label-> label to add to the graph; string
font-> font of the text
action->action associated with label
label_maxlen-> maximum number of letters to be added in one line
colour-> colour
NOTE: the text in the label has to end with a space otherwise the function will not work

7. Compile and run
To append all items to the screen:
s1.compile()
NOTE: any screen append statement after compile will not be added to the graph
To run the graph , the last line should be usf.run()

## To Import Your Own Graph:
use usf.set_key(str). here str is the set of letters on the graph you want to import after the /calculator/ in the url

## To save the graph
the graph runs in an instance of chromium. To save the graph and use extensions on it, login to your account, save the graph and you can access and run it in a browser with your chosen extensions

## To Add Your own blocks using add_exp
Refer to the usf script documentation to see how to add images, letters etc

## Recommended extentions
desmos godmode-> taper monke script to bypass list limit and recursion limits ->https://gist.github.com/jared-hughes/1bab5d94e2ad0ab326180a21e3f955c0

Demodder-> installabe extension
