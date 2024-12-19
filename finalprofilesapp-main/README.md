How to run this GUI
Steps:
1) Link the repository to a folder on your pc.
2) Make sure you have npm installed on your pc.
3) Go onto AWS and go to amplify, go to create new app.
4) Choose deploy app with github, and chose this repository, then leave the rest of the settings alone and click save and deploy.
5) The app should be installed, and can now be run from the domain given in AWS Amplify. To run it on the local machine, go to the folder from step 1 in a command prompt terminal and run the command "npm run dev"
    - From there, you can use ctrl+o or copy the link to open the app, use ctrl+q to quit.

Notes:
    - The API gateway link is not set correctly, and therefore does not work right now, only the GUI component works, but theoretically all that is needed is to put in the correct API gateway endpoint link for the GUI to work as intended.
    - Whenever the repository is pushed to, the app will redeploy with the updated files.
