# BuildTool

<h2>Custom Build tool written in Python for building projects with complex build strategy</h2>

<h3>Currently supports only {NS} builds and testing for Android and iOS platforms</h3>

<h3>{NS} setup</h3>
<p>Clone the repository. Project requires a set of dependencies to install: </ br>
	<ul>
	<li>schedule</li>
	</ul></ br>
	When you created python environment run the project for the first time (it should fail, because you need to configure the Build Tool!!!).
	Go into `C:\Users\{system_user}\AppData\Local\BuildTool` (if on windows) or `/usr/local/bin/BuildTool` (if on *nix).
	Enter the details required in the configuration file. <b>Remember!</b> set your timer in minutes and generate GitHub access token, otherwise Build Tool with fail to 
	access the repository.
</p>
<p>
	If you have any special building rules that need to take place after dependency install and before build/test, create a new class extending Rule base class; implement
	execute_rule() method with your custom build logic. RUN!!
</p>