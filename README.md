WAMITurk
========

WAMITurk is a combination of different technologies used to enhance speech recognition training through crowdsourcing. This was my senior project at MIT with the Spoken Language Systems group. My research advisor was Prof. James Glass with the help from Ian McGraw.

Abstract
--------

Training data for spoken language systems can be scarce, and difficult to collect due to the expert guidance overhead. Through crowdsourcing technologies, such as Amazon Mechanical Turk, we can alleviate the need for experts by allowing users across the web to utter phrases in exchange for a micropayment of just a few cents. We present a mobile device framework for collecting speech data from Android users through Amazon Mechanical Turk. We collect and analyze several thousand utterances acquired through this framework. We then provide future strategies for other developers who are facing dilemmas involving speech collection for mobile devices.

Code
----

WAMITurk utilizes several different platforms and technologies in order to achieve its goal.

### Android

The purpose of the Android application is to attach hooks that will replace the regular Flash-based WAMI interface with Android controls. This is because not all smartphone browsers support Flash or give the browser permission to use the microphone. The application introduces a new entry in the javascript namespace in order to allow the web interface to properly control the application. The audio will get sent to the Appspot server. The android code will unfortunately not be published yet. The application can be found on the Google Play Store.

### Appspot

With Google Appspot, we were able to host the site that would be used for displaying a user interface and POSTing the audio collected from the user. The android application will overwrite the original WAMI controls. This Appspot server stores the audio blobs.

### Amazon Mechanical Turk

Through this we can gather a community of English speakers to speak certain phrases for a micropayment. We get a list of users who have attempted our hit and pay them accordingly.

### Data Collector

This code aggregates the results from Amazon Mechanical Turk and Appspot in order to place them in their proper directories. At the same time we can retrieve several useful results that allow us to make conclusions and inferences over certain topics (mentioned in my paper). We can also use this to see if anyone had tried to cheat us by not attempting a hit.

Paper
------

Link to my actual paper with more details will be posted soon.