<?php
    /*
        File Path:      /system/ci/system/amfphp/services/LaunchRPC.php
        Comments:
            This file is an amfphp rpc server.
    */
    
    //----------------------------------------------------------------------------------------------------
    // CI MODEL OPENER START
    
    // This will store all the global config data for LaunchCMS.  One var to rule them all!  (And not pollute the global namespace too much)
    global $LAUNCH;
    $LAUNCH = array();
    $LAUNCH["paths"] = array();
    
    // Initial "root" directory setup
    $arrLaunchRoot = explode("system/amfphp", dirname(__FILE__));
    $LAUNCH["paths"]["launch"] = $arrLaunchRoot[0];
    
    // Setting up the current launchcms/ root URL; domain and all
    $arrCurrentDir = explode("system/amfphp", dirname($_SERVER["PHP_SELF"]));
    $strCurrentDir = $arrCurrentDir[0];
    if ( $strCurrentDir{strlen($strCurrentDir) - 1} == "/" ) $strCurrentDir = substr($strCurrentDir, 0, -1);
    if ( isset($_SERVER['HTTPS']) ) $LAUNCH["root_url"] = 'https://' . $_SERVER['HTTP_HOST'] . $strCurrentDir."/";
    else $LAUNCH["root_url"] = 'http://' . $_SERVER['HTTP_HOST'] . $strCurrentDir."/";
    
    // This file contains global variables to all our paths.
    require_once($LAUNCH["paths"]["launch"]."config/paths.php");
    
    // These file allows us to access CI models without having to go through CI
    require_once($LAUNCH["paths"]["cimodel"].'ci_model_remote_open.php');
    
    // CI MODEL OPENER END
    //----------------------------------------------------------------------------------------------------



    // Create new service for PHP Remoting as Class
    // Extends LaunchCMS because it gives us access to all CI libraries as well as our DB model
    class LaunchRPC extends LaunchCMS {
    
    
        // If they fail authentication, we're going to send this back as a result
        var $arrBadAuth = array();
        
        
        function LaunchRPC () {

            // Calling the LaunchCMS constructor which calls the Model constructor...etc...
            parent::LaunchCMS();
            
            // Setting up our response to a bad authentication
            $this->arrBadAuth[0]->auth = "FALSE";
            
            // Define the methodTable for this class in the constructor
            $this->methodTable  =   array(
            
                "adminLogin"        =>  array(  "description"   =>  "Return auth information if they're legit",
                                                "access"        =>  "remote"),
                "getAdminSession"   =>  array(  "description"   =>  "Checked if there is a session or cookie set for the users login information and returns it",
                                                "access"        =>  "remote"),
                "adminLogout"       =>  array(  "description"   =>  "Logs the admin user out and removes all the session/cookie information for their account",
                                                "access"        =>  "remote"),
                "dbDelete"          =>  array(  "description"   =>  "Deletes data in the DB",
                                                "access"        =>  "remote"),
                "dbInsert"          =>  array(  "description"   =>  "Inserts information into the DB",
                                                "access"        =>  "remote"),
                "dbSelect"          =>  array(  "description"   =>  "Returns general information to the admin panel",
                                                "access"        =>  "remote"),
                "dbUpdate"          =>  array(  "description"   =>  "Updates data in the DB",
                                                "access"        =>  "remote"),
                "getLang"           =>  array(  "description"   =>  "Retrives the language preference from the DB",
                                                "access"        =>  "remote"),
                "getDirListing"     =>  array(  "description"   =>  "Retrives the directory listing from filestore",
                                                "access"        =>  "remote"),
                "getCustomListing"  =>  array(  "description"   =>  "Gets a custom passed in directory listing based on the launch root.",
                                                "access"        =>  "remote"),
                "getThemeListing"   =>  array(  "description"   =>  "Retrives the directory listing for the themes directory",
                                                "access"        =>  "remote"),
                "getLoginLogoURL"   =>  array(  "description"   =>  "Gets the URL of the login logo",
                                                "access"        =>  "remote"),
                "createDir"         =>  array(  "description"   =>  "Creates a directory",
                                                "access"        =>  "remote"),
                "moveToTrash"       =>  array(  "description"   =>  "Moves a file or folder to the trash can",
                                                "access"        =>  "remote"),
                "moveFileOrFolder"  =>  array(  "description"   =>  "Moves a file or folder another folder",
                                                "access"        =>  "remote"),
                "deleteFileOrFolder"=>  array(  "description"   =>  "Deletes a file or folder",
                                                "access"        =>  "remote"),
                "renameFileOrFolder"=>  array(  "description"   =>  "Renames a file or folder",
                                                "access"        =>  "remote"),
                "emptyTrash"        =>  array(  "description"   =>  "Empties the current users trash",
                                                "access"        =>  "remote"),
                "phpSettings"       =>  array(  "description"   =>  "Returns a list of pre-defined php settings",
                                                "access"        =>  "remote"),
                "getPluginListing"  =>  array(  "description"   =>  "Returns a listing of the contents of the plugins directory",
                                                "access"        =>  "remote"),
                "changePluginStatus"=>  array(  "description"   =>  "enables/installs or disabled a plugin",
                                                "access"        =>  "remote")
                                        );
            
        }
        
        
        
        // This function will see if the user already has a session or cookie data with login information
        function getAdminSession() {
            
            // Starting the session if it's not started yet.
            if ( !isset($_SESSION) ) session_start();
            
            // Getting the username and authstring if it's set, returning false if not
            if ( isset($_SESSION["auth_data"]["un"]) && isset($_SESSION["auth_data"]["as"]) ) {
                $strUserName = $_SESSION["auth_data"]["un"];
                $strAuthString = $_SESSION["auth_data"]["as"];
            }
            else {
                // Loading the cookie helper so we can check for auth cookies
                $this->load->helper('cookie');
                
                if ( get_cookie("un") && get_cookie("as") ) {
                    $strUserName = get_cookie("un");
                    $strAuthString = get_cookie("as");
                }
                else return false;
            }
            
            // Seeing if the user is authorized to login here
            $objUserData = $this->authUser($strUserName, $strAuthString, true);
            
            // If the returned auth information is false, returning false
            if ( !$objUserData ) return false;
            
            // The user was authorized, getting their information
            $objReturnAuth = $this->getSecurityData($objUserData);
            $objReturnAuth = $this->getUserData($objReturnAuth);
            $this->getBackgroundInfo($objReturnAuth);
            $this->getURLInfo($objReturnAuth);
            $objReturnAuth->auth_string = $strAuthString;
            
            return $objReturnAuth;
        
        }
        
    
        
        // This function logs admins in
        function adminLogin($arrLogin) {
            
            $objLoginData = $this->loginUser($arrLogin[0], $arrLogin[1], true);
            
            if ( !$objLoginData ) return false;
        
            // Getting the user's background preferences
            $this->getBackgroundInfo($objLoginData);
            
            // Starting the session if it's not started yet.
            if ( !isset($_SESSION) ) session_start();
            
            
            // Saving the login information in a session
            $_SESSION["auth_data"] = array();
            $_SESSION["auth_data"]["un"] = $objLoginData->username;
            $_SESSION["auth_data"]["as"] = $objLoginData->auth_string;
            
            
            // $arrLogin[2] is a boolean which sets "remember me" or not
            // If they want to be remembered, we save a cookie
            if ( isset($arrLogin[2]) && $arrLogin[2] == true ) {
                // Loading the cookie helper
                $this->load->helper('cookie');
                
                $unCookie = array( 'name' => 'un', 'value' => $varAuth[0]->username, 'expire' => '31556926' );
                set_cookie($unCookie);
                
                $asCookie = array( 'name' => 'as', 'value' => $varAuth[0]->auth_string, 'expire' => '31556926' );
                set_cookie($asCookie);
                
                $objLoginData->cookie = "set";
            }
            
            // Returning login information.  
            return $objLoginData;
            
        }
        
        
        
        // This function will setup/get the interface background information that the user has set
        function getBackgroundInfo( &$objLoginData ) {
        
            // Setting up a db query to pull in the background information the user has specified
            $this->db->select("name, value");
            $this->db->from("settings_users");
            $this->db->where("app = 'base' AND users_id = '".$objLoginData->users_id."' AND (name = 'background_img' OR name = 'background_grad')");
            $arrBGInfo = $this->select();
            
            // if there was an item set for the background type and for the background itself, we want to pull out the values and return them
            if ( count($arrBGInfo) > 0 ) {
                // Looping through all the returned values and setting the type and background
                for ( $i = 0 ; $i < count($arrBGInfo); $i++ ) {
                    if ( $arrBGInfo[$i]->name == "background_grad" ) {
                        $objLoginData->background_grad = $arrBGInfo[$i]->value;
                    }
                    elseif ( $arrBGInfo[$i]->name == "background_img" ) {
                        $objLoginData->background_img = $arrBGInfo[$i]->value;
                    }
                }
            }
            // There were no rows in the DB containing the background image data
            else {
                // Inserting the background gradient data
                $data = array(
                   'users_id' => $objLoginData->users_id,
                   'name' => 'background_grad',
                   'value' => '3368601|3394815',
                   'app' => 'base'
                );
                $this->db->insert('settings_users', $data);
                // Inserting the background image data
                $data = array(
                   'users_id' => $objLoginData->users_id,
                   'name' => 'background_img',
                   'value' => '',
                   'app' => 'base'
                );
                $this->db->insert('settings_users', $data);
                
                // Setting the background information that we'll be returning
                $objLoginData->background_img = "";
                $objLoginData->background_grad = "3368601|3394815";
            }
        
        }
        
        
        
        // This will get the URL and root-url and pass them back.
        function getURLInfo( &$objLoginData ) {
        
            global $LAUNCH;
        
            
            $objLoginData->root_url = $LAUNCH["root_url"];
            $objLoginData->url = $LAUNCH["root_url"] . "?l=";
            
            // Defaulting clean urls to false
            $boolCleanURLS = false;
                
            if ( in_array("mod_rewrite", apache_get_modules()) ) {
            
                // Checking for the .htaccess file
                if ( file_exists($LAUNCH["paths"]["launch"].".htaccess") ) {
                    
                    // If we find our 'index.php?l=' that's reason enough to believe they've put the correct .htaccess file together
                    if ( strstr(file_get_contents($LAUNCH["paths"]["launch"].".htaccess"), "index.php?l=") ) {
                        $boolCleanURLS = true;
                    }
                }
            }
                
            // If clean urls are NOT enabled, we want to append the location string "?l=" to the end of the root URL.
            $objLoginData->url = $LAUNCH["root_url"];
            if ( !$boolCleanURLS ) $objLoginData->url .= "?l=";
            
        }
        
        
        
        
        // Logs the admin user out and removes all the session/cookie information for their account
        function adminLogout($arrAuthInfo) {
            
            if ( !$this->authUser($arrAuthInfo[0], $arrAuthInfo[1], true) ) return false;
            
            // Starting the session if it's not started yet.
            if ( !isset($_SESSION) ) session_start();
            
            // Loading the cookie helper
            $this->load->helper('cookie');
            
            // Clearing all sessions and cookies having to do with the user's login
            $_SESSION["auth_data"] = array();
            delete_cookie("un");
            delete_cookie("as");
            
            return true;
            
        }
        
        
        
        
        
        // This is for deleting data from the DB
        function dbDelete($arrParams) {
        
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
                
                $arrResult = array();
            
                if ( $this->delete($arrParams[2], $arrParams[3]) ) {
                    $arrResult[0]->success = "TRUE";
                    return $arrResult;
                }
                else {
                    $arrResult[0]->success = "FALSE";
                    return $arrResult;
                }
                
            } else return $this->arrBadAuth;
        
        }
        
        
        
        // This is for general insertion of data
        function dbInsert($arrParams) {
        
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
            
                $arrInsertParams = array();
                
                // Setting up the array of parameters to be inserted
                for ( $i = 0; $i < count($arrParams[3][0]); $i++ ) {
                    
                    // Setting the element name and value to the values of the elements of their array
                    $this->db->set($arrParams[3][0][$i], $arrParams[3][1][$i]);
                    
                }

                $arrResult = array();
            
                if ( $this->db->insert($arrParams[2]) ) {
                    
                    // We want to set and return the ID of the new record we just added if $arrParams[4] is set
                    if ( isset($arrParams[4]) && $arrParams[4] != "" ) {
                        $this->db->select($arrParams[4]);
                        $this->db->from($arrParams[2]);
                        $this->db->limit(1);
                        $this->db->orderby($arrParams[4], "desc");
                        $arrIDResult = $this->select(null);
                        $arrResult[0]->newID = $arrIDResult[0]->$arrParams[4];
                    }
                    
                    $arrResult[0]->success = "TRUE";
                    return $arrResult;
                    
                }
                else {
                    $arrResult[0]->success = "FALSE";
                    return $arrResult;
                }
            
            } else return $this->arrBadAuth;
        
        }
        
        
        
        // This is for general selection and returning of values.
        function dbSelect($arrParams) {
        
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
                
                // Removing the user name and auth string since we don't need them anymore
                // the $this->select() function doesn't like them either ;)
                array_shift($arrParams);
                array_shift($arrParams);
                
                return $this->select($arrParams);
                
            } else return $this->arrBadAuth;
            
        }
        
        
        
        // This is for updating information in the database
        function dbUpdate($arrParams) {
        
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
            
                $arrInsertParams = array();
                
                // Setting up the array of parameters to be updated
                for ( $i = 0; $i < count($arrParams[3][0]); $i++ ) {
                    
                    // Setting the element name and value to the values of the elements of their array
                    $this->db->set($arrParams[3][0][$i], $arrParams[3][1][$i]);
                    
                }
                
                $arrResult = array();
                
                $this->db->where($arrParams[4]);
            
                if ( $this->db->update($arrParams[2]) ) {
                    $arrResult[0]->success = "TRUE";
                    return $arrResult;
                }
                else {
                    $arrResult[0]->success = "FALSE";
                    return $arrResult;
                }
            
            } else return $this->arrBadAuth;
            
        }
        
        
        
        // This will return the language preference set up in the base DB table
        function getLang() {
        
            // Setting up the db query
            $this->db->select("value");
            $this->db->from("settings_global");
            $this->db->where("name", "language");
            $this->db->where("app", "base");
            
            // Getting the information from the DB.
            $arrDefaultLanguage = $this->select(null);
    
            return $arrDefaultLanguage[0]->value;
        
        }
        
        
        // Returns the path to the login logo url
        function getLoginLogoURL() {
        
            // Setting up the db query
            $this->db->select("value");
            $this->db->from("settings_global");
            $this->db->where("name", "login_logo_url");
            $this->db->where("app", "base");
            
            // Getting the information from the DB.
            $arrDefaultLanguage = $this->select();
    
            return $arrDefaultLanguage[0]->value;
                    
        }
        
        
        
        // This will return an object full of php settings that we want to send back
        function phpSettings($arrParams) {
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
            
                // Getting the max upload file size and max post size and replacing M/K with their integer values
                $umf = str_replace("K", "000", str_replace("M", "000000", ini_get('upload_max_filesize')));
                $pms = str_replace("K", "000", str_replace("M", "000000", ini_get('post_max_size')));
                // Saving the smaller of the two because this is the small-limit on a file-upload size
                if ( $umf < $pms ) $objResponse->intMaxFileSize = $umf;
                else $objResponse->intMaxFileSize = $pms;
                
                $sm = ini_get('safe_mode');
                if ( $sm == "0" || strtolower($sm) == "off" ) $objResponse->boolSafeMode = false;
                else $objResponse->boolSafeMode = true;
                
                return $objResponse;
                
            } else return $this->arrBadAuth;
        }
        
        
        
        
        
        /*-------------------------------------------------------//
        //-- THESE FUNCTIONS ARE FOR FILE/DIRECTORY OPERATIONS --//
        //-------------------------------------------------------*/
        
        
        // This function will retrieve a directory listing from the filestore folder
        function getDirListing($arrParams) {
        
            if ( !$this->authUser($arrParams[0], $arrParams[1], true) ) return $this->arrBadAuth;
                
            global $LAUNCH;
            
            // Creating the main user directory if it doesn't exist, and filling it with optional directories
            if ( !is_dir($LAUNCH["paths"]["userfiles"].$arrParams[0]) ) {
                mkdir($LAUNCH["paths"]["userfiles"].$arrParams[0], 0777);
                // the mkdir doesn't always properly set the permissions to 0777 so we're gonna chmod it ourselves
                chmod($LAUNCH["paths"]["userfiles"].$arrParams[0], 0777);
            }
            
            // Making sure the main two folders exists inside the USER'S folder
            $arrUserDirs = array("default","home");
            for ( $i = 0; $i < count($arrUserDirs); $i++ ) {
                if ( !is_dir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/".$arrUserDirs[$i]) ) {
                    mkdir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/".$arrUserDirs[$i], 0777);
                    chmod($LAUNCH["paths"]["userfiles"].$arrParams[0]."/".$arrUserDirs[$i], 0777);
                }
            }
            
            // Making sure the required two folders exists inside the USER'S DEFAULT folder
            $arrDefaultUserDirs = array("Desktop","Trash");
            for ( $i = 0; $i < count($arrDefaultUserDirs); $i++ ) {
                if ( !is_dir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/".$arrDefaultUserDirs[$i]) ) {
                    mkdir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/".$arrDefaultUserDirs[$i], 0777);
                    chmod($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/".$arrDefaultUserDirs[$i], 0777);
                }
            }
            
            // Making sure the main four folders exists inside the SHARE folder
            $arrInternalShareDirs = array("Documents","Images","Audio-Video","Library");
            for ( $i = 0; $i < count($arrInternalShareDirs); $i++ ) {
                if ( !is_dir($LAUNCH["paths"]["share"].$arrInternalShareDirs[$i]) ) {
                    mkdir($LAUNCH["paths"]["share"].$arrInternalShareDirs[$i], 0777);
                    chmod($LAUNCH["paths"]["share"].$arrInternalShareDirs[$i], 0777);
                }
            }
            
            // Making sure the Backgrounds folder exists in the images folder
            if ( !is_dir($LAUNCH["paths"]["share"]."Images/Backgrounds") ) {
                mkdir($LAUNCH["paths"]["share"]."Images/Backgrounds", 0777);
                // the mkdir doesn't always properly set the permissions to 0777 so we're gonna chmod it ourselves
                chmod($LAUNCH["paths"]["share"]."Images/Backgrounds", 0777);
            }
            
                            
            // This will allow us to do directory operations
            $this->load->helper('directory');
            
            $objReturnData->objDirMap = directory_map($LAUNCH["paths"]["filestore"]);
            
            return $objReturnData;
            
        }
        
        
        
        // This will get us a custom directory listing based on the launch root.
        function getCustomListing($arrParams) {
        
            if ( !$this->authUser($arrParams[0], $arrParams[1], true) ) return $this->arrBadAuth;
            
            global $LAUNCH;
            
            // This will allow us to do directory operations
            $this->load->helper('directory');
            
            if ( is_dir($LAUNCH["paths"]["launch"].$arrParams[2]) ) return directory_map($LAUNCH["paths"]["launch"].$arrParams[2], true);
            else return array();
        
        }
        
        
        
        // This will grab the theme listing for us so we can use it in the 
        function getThemeListing($arrParams) {
            
            if ( !$this->authUser($arrParams[0], $arrParams[1], true) ) return $this->arrBadAuth;
            
            global $LAUNCH;
            
            $this->load->helper('directory');
            
            $arrThemeDirMap = directory_map($LAUNCH["paths"]["themes"], true);
            
            // This will hold the final theme listing.
            $arrThemeList = array();
            
            // Looping through each plugin and making sure all the files are in place and getting its info.xml file
            for ( $i = 0, $max = count($arrThemeDirMap); $i < $max; $i++ ) {
                // If the dir mapped item is a folder, we treat it as a theme, otherwise we ignore it.
                if ( is_dir($LAUNCH["paths"]["themes"].$arrThemeDirMap[$i]) ) array_push($arrThemeList, $arrThemeDirMap[$i]);
            }
            
            return $arrThemeList;
            
        }
        
        
        
        // This function will create a directory
        function createDir($arrParams) {
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
            
                global $LAUNCH;
                
                if ( !is_dir($LAUNCH["paths"]["filestore"].$arrParams[2]."/".$arrParams[3]) ) {
                    mkdir($LAUNCH["paths"]["filestore"].$arrParams[2]."/".$arrParams[3], 0777);
                    chmod($LAUNCH["paths"]["filestore"].$arrParams[2]."/".$arrParams[3], 0777);
                    return true;
                }
                else return false;
            
            } else return $this->arrBadAuth;
        }
        
        
        
        // This function will move a file/directory to the trash
        function moveToTrash($arrParams) {
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
            
                global $LAUNCH;
                
                // The Trash Directory is manditory and will always be assured to be created
                if ( !is_dir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/Trash") ) {
                    mkdir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/Trash", 0777);
                    chmod($LAUNCH["paths"]["userfiles"].$arrParams[0]."/Trash", 0777);
                }
                
                // Making sure this file/folder doesn't already exist in the Trash
                if ( !is_dir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash/".$arrParams[3]) && !is_file($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash/".$arrParams[3]) ) {
                    
                    // Making sure the user isn't trying to delete the Desktop or the Trash
                    if ( ($LAUNCH["paths"]["filestore"].$arrParams[2]."/".$arrParams[3] != $LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash") && ($LAUNCH["paths"]["filestore"].$arrParams[2]."/".$arrParams[3] != $LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Desktop") ) {

                        // "renaming" our item into the trash
                        rename($LAUNCH["paths"]["filestore"].$arrParams[2]."/".$arrParams[3], $LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash/".$arrParams[3]);
                        // returning success or failure
                        if ( is_dir($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash/".$arrParams[3]) || is_file($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash/".$arrParams[3]) ) return true;
                        else return false;
                        
                    } else return false;
                    
                } else return false;
                
            } else return $this->arrBadAuth;
        }
        
        
        
        // This function will move a file/directory to a specific location
        function moveFileOrFolder($arrParams) {
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
                
                global $LAUNCH;
            
                // The location we're moving from, + the item name that's getting moved
                $strMoveFrom = $arrParams[2];
                $arrMoveFromArray = explode("/", $strMoveFrom);
                // The name of the item we're moving
                $strItemToMove = $arrMoveFromArray[count($arrMoveFromArray) - 1];
                
                // The location we're moving the item to
                $strMoveTo = $arrParams[3];
                
                if ( !is_dir($LAUNCH["paths"]["filestore"].$strMoveTo."/".$strItemToMove) && !is_file($LAUNCH["paths"]["filestore"].$strMoveTo."/".$strItemToMove) ) {
                    
                    // "renaming" our item to the new location
                    rename($LAUNCH["paths"]["filestore"].$strMoveFrom, $LAUNCH["paths"]["filestore"].$strMoveTo."/".$strItemToMove);
                    // returning success or failure
                    if ( is_dir($LAUNCH["paths"]["filestore"].$strMoveTo."/".$strItemToMove) || is_file($LAUNCH["paths"]["filestore"].$strMoveTo."/".$strItemToMove) ) return true;
                    else return false;
                    
                } else return false;
                
            
            } else return $this->arrBadAuth;
        }
        
        
        
        // This function will delete a passed in file or folder
        function deleteFileOrFolder($arrParams) {
        
            if ( !$this->authUser($arrParams[0], $arrParams[1], true) ) return $this->arrBadAuth;
            
            global $LAUNCH;
            
            // Checking if this is a file
            if ( is_file($LAUNCH["paths"]["filestore"].$arrParams[2]) ) {
                
                // returning true of the file is deleted successfully
                if ( unlink($LAUNCH["paths"]["filestore"].$arrParams[2]) ) return true;
                else return false;
            
            }
            // Checking if this is a folder
            if ( is_dir($LAUNCH["paths"]["filestore"].$arrParams[2]) ) {
                
                // returning true if the folder is deleted successfully
                if ( rmdir($LAUNCH["paths"]["filestore"].$arrParams[2]) ) return true;
                else return false;
            
            }
            // If it's not a file or folder, we return false.
            else return false;
        
        }
        
        
        
        // This function will rename a file/directory
        function renameFileOrFolder($arrParams) {
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
                
                global $LAUNCH;
                
                $strTarget = $arrParams[2];
                $arrTargetArray = explode("/", $strTarget);
                $strOldFileName = array_pop($arrTargetArray);   // Saving the old "target" and removing it from the target array
                $strNewFileName = $arrParams[3];
                $strTarget = implode("/", $arrTargetArray);     // Combining the target array into one string
                
                // making sure it doesn't already exist
                if ( !is_dir($LAUNCH["paths"]["filestore"].$strTarget."/".$strNewFileName) && !is_file($LAUNCH["paths"]["filestore"].$strTarget."/".$strNewFileName) ) {
                    
                    //renaming our item
                    rename($LAUNCH["paths"]["filestore"].$strTarget."/".$strOldFileName, $LAUNCH["paths"]["filestore"].$strTarget."/".$strNewFileName);
                    
                    // Making sure the item renamed properly
                    if ( is_dir($LAUNCH["paths"]["filestore"].$strTarget."/".$strNewFileName) || is_file($LAUNCH["paths"]["filestore"].$strTarget."/".$strNewFileName) ) return true;
                    else return false;
                    
                } else return false;
                
            } else return $this->arrBadAuth;
        }
        
        
        
        // this function will empty the current users trash
        function emptyTrash($arrParams) {
            if ( $this->authUser($arrParams[0], $arrParams[1], true) ) {
            
                global $LAUNCH;
                
                // Emptying the trash directory of this user
                if ( $this->emptyDirectory($LAUNCH["paths"]["userfiles"].$arrParams[0]."/default/Trash", true) ) return true;
                else return false;
                
            } else return $this->arrBadAuth;
        }
        
        

        // --------  Recursive Directory Delete PHP function ---------
        // Got this from http://www.dreamincode.net/code/snippet1225.htm
        function emptyDirectory($directory, $empty=FALSE) {
        
             // if the path has a slash at the end we remove it here
             if(substr($directory,-1) == '/') {
                  $directory = substr($directory,0,-1);
             }
             // if the path is not valid or is not a directory ...
             if(!file_exists($directory) || !is_dir($directory)) {
                  // ... we return false and exit the function
                  return FALSE;
             }
             // ... if the path is not readable
             elseif (!is_readable($directory)) {
                  // ... we return false and exit the function
                  return FALSE;
             }
             // ... else if the path is readable
             else {
                  // we open the directory
                  $handle = opendir($directory);
                  // and scan through the items inside
                  while (FALSE !== ($item = readdir($handle))) {
                       // if the filepointer is not the current directory
                       // or the parent directory
                       if($item != '.' && $item != '..') {
                            // we build the new path to delete
                            $path = $directory.'/'.$item;
                            // if the new path is a directory
                            if(is_dir($path)) {
                                 // we call this function with the new path
                                 $this->emptyDirectory($path);
                            // if the new path is a file
                            }
                            else {
                                 // we remove the file
                                 unlink($path);
                            }
                       }
                  }
                  // close the directory
                  closedir($handle);
                  // if the option to empty is not set to true
                  if($empty == FALSE) {
                       // try to delete the now empty directory
                       if(!rmdir($directory)) {
                            // return false if not possible
                            return FALSE;
                       }
                  }
                  // return success
                  return TRUE;
             }
        }
        // ------------------------End Of Function----------------------------
        
        
        
        
        /*-----------------------------------------------//
        //-- THESE FUNCTIONS ARE FOR PLUGIN OPERATIONS --//
        //-----------------------------------------------*/
        
        // This function will return a directory listing of the plugins directory as well as set up anything that needs to be set up for the plugins table
        function getPluginListing($arrParams) {
            if ( !$this->authUser($arrParams[0], $arrParams[1], true) ) return $this->arrBadAuth;
            
            global $LAUNCH;
            
            // This will allow us to do directory operations
            $this->load->helper('directory');
            $this->load->helper('launch_xml_reader');
                        
            
            
            /* -- PLUGIN DIRECTORY HANDLING -- */
            // Getting the directory listing of the plugins directory
            $arrDirPlugins = directory_map($LAUNCH["paths"]["plugins"], true);
            
            // Looping through each plugin and making sure all the files are in place and getting its info.xml file
            for ( $i = 0, $max = count($arrDirPlugins); $i < $max; $i++ ) {
                
                // Making sure each item in the plugins directory is a directory and has the needed files in it.
                if (    is_dir($LAUNCH["paths"]["plugins"].$arrDirPlugins[$i]) &&
                        is_file($LAUNCH["paths"]["plugins"].$arrDirPlugins[$i]."/info.xml") &&
                        is_file($LAUNCH["paths"]["plugins"].$arrDirPlugins[$i]."/index.php") )  {
                    
                    
                    // Holding on to the directory name so we can use it later.
                    $strPluginDir = $arrDirPlugins[$i];
                    
                    // Getting the plugin's information from its xml file.
                    $arrPluginData = xml2array( file_get_contents($LAUNCH["paths"]["plugins"].$arrDirPlugins[$i]."/info.xml") );
                    $key = array_keys($arrPluginData);
                    $arrDirPlugins[$i] = $arrPluginData[$key[0]];
                    
                    // Saving the original directory name as part of the directory attributes
                    $arrDirPlugins[$i]["dir"] = $strPluginDir;
                
                }
                else unset($arrDirPlugins[$i]);
                
            }
            // Reindexing the array of directory plugins
            $arrDirPlugins = array_values($arrDirPlugins);
            
            
            
            /* -- PLUGINS DB TABLE HANDLING -- */
            // Getting all the plugins out of the database that are currently in there.
            $this->db->from("plugins");
            $arrDBPlugins = $this->select();
            
            // Removing any plugins from the database that are no longer in the plugins directory
            for ( $i = 0, $max = count($arrDBPlugins); $i < $max; $i++ ) {
            
                $boolInPluginList = false;
                
                foreach ( $arrDirPlugins as $arrDirPlugin ) {
                    if ( $arrDirPlugin["name"] == $arrDBPlugins[$i]->name ) $boolInPluginList = true;
                }
                
                // If the plugin from the database isn't in the list of plugins, we want to remove it from the database
                if ( !$boolInPluginList ) {
                    $this->db->where("plugin_id", $arrDBPlugins[$i]->plugin_id);
                    $this->db->delete("plugins");
                    unset($arrDBPlugins[$i]);
                }
            
            }
            //Reindexing the array of db plugins
            $arrDBPlugins = array_values($arrDBPlugins);
            
            
            
            /* -- PLUGINS DIR AND DB SYNCING -- */
            // Looping through every plugin directory and making sure it's been added to the database.
            for ( $i = 0, $max = count($arrDirPlugins); $i < $max; $i++ ) {
                
                $boolPluginInDB = false;
                
                // Adding the "enabled" value to the plugin and setting it to the default value
                // If the plugin is already in the database, this value will be updated based on the stored value
                $arrDirPlugins[$i]["enabled"] = "0";
                
                // Looping through each db plugin and seeing if a plugin in the dir is also installed in the database
                // If it's in the DB, we want to get whatever its enabled status is.
                foreach ( $arrDBPlugins as $objDBPlugin ) {
                    if ( $objDBPlugin->name == $arrDirPlugins[$i]["name"] ) {
                        $boolPluginInDB = true;
                        $arrDirPlugins[$i]["enabled"] = $objDBPlugin->enabled;
                    }
                }
                
                // If the directory plugin isn't in the DB, we want to insert it into the plugins table
                if ( !$boolPluginInDB ) {
                
                    $arrData = array(
                        "display_name"  =>  $arrDirPlugins[$i]["display_name"],
                        "dir"           =>  $arrDirPlugins[$i]["dir"],
                        "name"          =>  $arrDirPlugins[$i]["name"],
                        "description"   =>  $arrDirPlugins[$i]["description"],
                        "version"       =>  $arrDirPlugins[$i]["version"],
                        "url"           =>  $arrDirPlugins[$i]["url"]
                    );
                    $this->db->insert("plugins", $arrData);
                    
                }
            
            }
            
            
            return $arrDirPlugins;
            
        }
        
        
        // This function will change a plugin's status
        function changePluginStatus($arrParams) {
            if ( !$this->authUser(array_shift($arrParams), array_shift($arrParams), true) ) return $this->arrBadAuth;
            
            global $LAUNCH;
            
            $intEnable = $arrParams[0];
            $strPlugin = $arrParams[1];
            
            // Getting the plugin in question out of the database.
            $this->db->from("plugins");
            $this->db->where("name", $strPlugin);
            $arrPlugin = $this->select();
            
            // Making sure we got one row from the database
            if ( count($arrPlugin) != 1 ) return false;
            else $objPlugin = $arrPlugin[0];
            
            
            // Setting the enabled value in the database to what we have passed in.
            $this->db->set("enabled", $intEnable);
            $this->db->where("name", $strPlugin);
            $this->db->update("plugins");
            
            
            // If we're enabling a plugin, we want to go through its installer process
            if ( $intEnable == "1" && file_exists($LAUNCH["paths"]["plugins"].$objPlugin->dir."/install.php") ) {
                
                require($LAUNCH["paths"]["plugins"].$objPlugin->dir."/install.php");
                
                if ( class_exists("install_".$strPlugin."_plugin") ) {
                    $install_plugin_class = "install_".$strPlugin."_plugin";
                    $objInstallPlugin = new $install_plugin_class();
                    
                    if ( method_exists($objInstallPlugin, "install") ) {
                        $strReturnString = $objInstallPlugin->install();
                        
                        // If the installer passed back a string, we return the string for the user's benefit
                        if ( is_string($strReturnString) ) return $strReturnString;
                    }
                
                }
            
            }
            elseif ( $intEnable == "0" ) return $objPlugin->display_name." Plugin Disabled.";
            
            return true;
            
        }
        

        
    }   // End of File