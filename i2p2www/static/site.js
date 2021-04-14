// Detect OS by user-agent and jump to header by ID.

document.addEventListener("DOMContentLoaded", function(event) {
	let detectedOS="windows";

	if (navigator.userAgent.indexOf("Windows")!=-1) detectedOS="windows";
	if (navigator.userAgent.indexOf("Macintosh")!=-1) detectedOS="mac";
	if (navigator.userAgent.indexOf("X11")!=-1) detectedOS="unix";
	if (navigator.userAgent.indexOf("Linux")!=-1) detectedOS="unix";
	if (navigator.userAgent.indexOf("Android")!=-1) detectedOS="android";

	document.getElementById(detectedOS).scrollIntoView();
});