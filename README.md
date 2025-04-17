make a tool that is able to allow user to create the script without interaction with code
- everything needs to be considered, font, images, location, highlights (inspect page)
make the code general, have a configuration file which could act like a dictionary to define variables
have an application to run those test scripts and create a summary of the test run
after all automation is complete, create another summary (one line) of all of the test runs covered
- areas covered by tests, number completed, number passed and failed
prioritize more on functionality but also on checking if elements are displayed properly

// TODO:
- implementation
develop all possible actions/commands that can be called
generalize them so it is less of them but more parameters
work on the check function so it could check for location, maybe font, text, maybe clickable *DONE
wait function, keep track of time *DONE

keep track of what page we are on by using states from an enumerator *DONE
depending on which state there will be various elemnents that should be present *DONE

determine a way to compare two images *DONE
- using the screenshot function take pictures of the current version and have already saved references *DONE
- compare those freshly taken screenshots and compare them with the references to determine differences *DONE
- find out if you can compare only certain sections of the pictures *DONE

form a queue with the test runs, upload multiple files *DONE
create tabs of each file and be able to edit them *DONE
when running the program, it goes through each one by one, in the order provided and then it stops *DONE

have a command that sends a serial API command from the application
in parallel have an output of the serial API results, have the console available
if the API console works, create a command to check if the correct results were outputted

maybe instead of key words, move towards giving the xpath the user provides


- GUI
have a working GUI that allows the script_generator to run *DONE
be able to write in a text box the available commands to form a test run *DONE
be able to import an already existing test run and run it *DONE
return some sort of summary to explain which part went wrong *DONE
be able to export a created test run *DONE

export the excel tab of each test run to display how many of their commands they passed *DONE

keep track of the terminal, instead of opening putty, have it displayed in another tab *DONE
add multiple tabs if possible, allows the user to add another wall controller or octroller logs *DONE

for the element dictionary, create a legend where the user can search for each desirable element
have a visualizer which displays where the elements would be located (using highlight)

add another instruction button for the commands, to explain what each represents
- one button to open up a word file that could contain all of the explanations
