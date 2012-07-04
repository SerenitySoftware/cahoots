<?php
    /*
        File Path:      /apps/form/system.php
        Comments:
            This file will handle the form app's form system
    */

    
    class form_system extends LaunchCMS {
        
        function form_system() {
            // Calling the LaunchCMS constructor which calls the Model constructor...etc...
            parent::LaunchCMS();
            
            $this->load->helper('email');
            $this->load->library('email');
            $this->_assign_libraries();
        }
        
        
        function contact_form($data) {
            
            if($data['error']) return form_error($data);
            else {

                // email
                if(!valid_email($data['email']['value'])) {
                    $data['email']['error'] = true;
                    $data['email']['error_message'] = "Please double check your email address.";
                    
                    return form_error($data);
                }
                
                
                // message
                $message  = 'From: '.$data['name']['value']."\n";
                $message .= 'Feeling: '.$data['feelings']['value']."\n\n";
                $message .= $data['comment']['value'];
                                
                //send message
                $this->email->from($data['email']['value'], $data['name']['value']);
                $this->email->to('joshua@launchcms.com'); 
                $this->email->subject('LaunchCMS Contact Form');
                $this->email->message($message);
                
                if(!$this->email->send()) {
                    $data['error_message']  = 'Your message could not be sent at this time.'; 
                    $data['error_message'] .= 'We are working to correct this problem as soon as possible. Thank you for your patience.';
                    $data['error_message'] .= '<pre>'.$this->email->print_debugger().'</pre>';
                    
                    return form_error($data);
                }
                
                // finalizing
                $data['success_message'] = 'Your message has been sent.';
                return form_success($data);
                
            }
        }
        
    }