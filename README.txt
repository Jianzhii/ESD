###########################################
Setting up Stonks Exchange on local machine
###########################################

Software requirements:
1. WAMP(windows)/ MAMP(MacOS)
2. Docker Desktop
3. Visual Studio Code (or your preferred IDE)

#################################
Steps to set up local environment
#################################

1. Start up WAMP/MAMP server and Docker Desktop
2. Unzip the downloaded Stonks Exchange app file into WAMP/MAMP webroot
3. Go to localhost/phpmyadmin on your web browser to create necesary schemas and user account for remote access from Docker with the following steps
	a. Inside phpMyAdmin, click on 'User accounts' 
	b. Select 'Add user account' and input the following:
		User name: Use text field, is213
		Host name: Any host, %
		Password: (Change to No Password)
	c. Select 'Data' under 'Global privileges' and click 'Go'
	d. After user is successfully created, click on 'SQL' and run commands inside 3 SQL files (funds.sql, portfolio.sql, profile.sql) 
 	   found in 'sql' folder in the unzipped file to create the necessary schemas
4. Check your MySQL port number (3306/ 3308) at the top bar of phpMyAdmin and note it down.
5. Inside the unzipped app file, open up 'docker-compose.yaml' inside the 'docker' folder using Visual Studio Code or your preferred IDE
6. Look for profile, funds and portfolio microservice and change the portnumber in 'dbURL' to the port number your MySQL is running on.
	e.g. mysql+mysqlconnector://is213@host.docker.internal:3306/profile OR
	     mysql+mysqlconnector://is213@host.docker.internal:3308/profile
7. Open up command prompt and navigate to 'docker' folder of the unzipped file inside your WAMP/MAMP webroot
8. Type in the command 'docker-compose up'
9. After all microservices are started up in command prompt, head over to your browser and go to http://localhost:1337 to configure API Gateway routing
   with the following steps:

	#################################################
	Steps to set up all API Gateway routing (Kong)
	#################################################

	# This is a one-time only set up as all your configuration will be saved to the postgre container so do not remove your postgre container if you are not using it.

	a. Register an account in Konga with your email and password
	b.Login with the email and password you just created
	c. After logging in, you will be prompted to connect Konga to Kong with the following inputs
    		Name: default
   	 	Kong Admin URL: http://kong:8001


	# Set up for user profile micro service
	d. Click service and create a new service with the following parameters:
    		Name: Userprofile
    		URL: http://user_profile:5008/userprofile
	e. After service is created, click into routes and click add a route with the following parameters:
    		Path: /api/v1/userprofile
    		Methods: GET

	# Set up for stock info micro service
	f. Click service and create a new service with the following parameters:
    		Name: stock_info
    		URL: http://yahoo_friend:5900/stock
	g. After service is created, click into routes and click add a route with the following parameters:
   		Path: /api/v1/stock
    		Methods: GET

	# Set up for market summary micro service
	h. Click service and create a new service with the following parameters:
    		Name: market_summary
    		URL: http://yahoo_friend:5900/market
	i. After service is created, click into routes and click add a route with the following parameters:
    		Path: /api/v1/market
    		Methods: GET

	# Set up for buy stocks micro service
	j. Click service and create a new service with the following parameters:
   		Name: buy_stocks
    		URL: http://order_management:5100/order/buy
	k. After service is created, click into routes and click add a route with the following parameters:
    		Path: /api/v1/order/buy
    		Methods: PUT OPTIONS

	# Set up for sell stocks micro service
	l. Click service and create a new service with the following parameters:
    		Name: sell_stocks
    		URL: http://order_management:5100/order/sell
	m. After service is created, click into routes and click add a route with the following parameters:
    		Path: /api/v1/order/sell
    		Methods: PUT OPTIONS

    
	# Set up for user authentication micro service
	n. Click service and create a new service with the following parameters:
    		Name: authUser
    		URL: http://auth_user:5200/auth
	o. After service is created, click into routes and click add a route with the following parameters:
    		Path: /api/v1/auth
    		Methods: POST OPTIONS

	# Set up for funds micro service
	p. Click service and create a new service with the following parameters:
    		Name: funds
    		URL: http://funds:5002/funds
	q. After service is created, click into routes and click add a route with the following parameters:
    		Path: /api/v1/funds
    		Methods: PUT OPTIONS

10. All configurations are done and Stonks Exchange is now working on your local machine.


Note: You will not be able to login with your personal email as authentication is required in our backend. 
      If you wish to continue with your personal email, please contact us, else you may use the following test account:
	username: g4t5stonksexchange@gmail.com
	password: StonksExchangeT5
      Ensure you allow all cookies in your browser to allow the Google Authentication to work. 