require "help/script_execution_state"
require "scripts/ec2/ec2_script"
require "help/remote_command_handler"
#require "help/dm_crypt_helper"
require "help/ec2_helper"
require "AWS"

# Creates a bootable EBS storage from an existing AMI.

class Ami2EbsConversion < Ec2Script
  # Input parameters
  # * aws_access_key => the Amazon AWS Access Key (see Your Account -> Security Credentials)
  # * aws_secret_key => the Amazon AWS Secret Key
  # * ami_id => the ID of the AMI to be converted
  # * security_group_name => name of the security group to start
  # * ssh_username => name of the ssh-user (default = root)
  # * ssh_key_data => Key information for the security group that starts the AMI [if not set, use ssh_key_files]
  # * ssh_key_files => Key information for the security group that starts the AMI
  # * remote_command_handler => object that allows to connect via ssh and execute commands (optional)
  # * ec2_api_handler => object that allows to access the EC2 API (optional)
  # * ec2_api_server => server to connect to (option, default is us-east-1.ec2.amazonaws.com)
  # * name => the name of the AMI to be created
  # * description => description on AMI to be created (optional)
  # * temp_device_name => [default /dev/sdj] device name used to attach the temporary storage; change this only if there's already a volume attacged as /dev/sdj (optional, default is /dev/sdj)
  # * root_device_name"=> [default /dev/sda1] device name used for the root device (optional)
  # * connect_trials => number of trials during ssh connect to machine
  # * connect_interval => seconds between two ssh connect trials
  def initialize(input_params)
    super(input_params)
  end

  def check_input_parameters()
    if @input_params[:security_group_name] == nil
      @input_params[:security_group_name] = "default"
    end
    if @input_params[:ami_id] == nil && !(@input_params[:ami_id] =~ /^ami-.*$/)
      raise Exception.new("Invalid AMI ID specified: #{@input_params[:ami_id]}")
    end
    ec2_helper = Ec2Helper.new(@input_params[:ec2_api_handler])
    if !ec2_helper.check_open_port(@input_params[:security_group_name], 22)
      raise Exception.new("Port 22 must be opened for security group #{@input_params[:security_group_name]} to connect via SSH")
    end
    if @input_params[:name] == nil
      @input_params[:name] = "Boot EBS (for AMI #{@input_params[:ami_id]}) at #{Time.now.strftime('%d/%m/%Y %H.%M.%S')}"
    else
    end
    if @input_params[:description] == nil
      @input_params[:description] = @input_params[:name]
    end
    if @input_params[:temp_device_name] == nil
      @input_params[:temp_device_name] = "/dev/sdj"
    end
    if @input_params[:root_device_name] == nil
      @input_params[:root_device_name] = "/dev/sda1"
    end
    if @input_params[:ssh_username] == nil
      @input_params[:ssh_username] = "root"
    end
    if @input_params[:connect_trials] == nil
      @input_params[:connect_trials] = 6
    end
    if @input_params[:connect_interval] == nil
      @input_params[:connect_interval] = 20
    end
  end

  def load_initial_state()
    Ami2EbsConversionState.load_state(@input_params)
  end
  
  private

  # Here begins the state machine implementation
  class Ami2EbsConversionState < ScriptExecutionState
    def self.load_state(context)
      state = context[:initial_state] == nil ? InitialState.new(context) : context[:initial_state]
      state
    end

  end

  # Nothing done yet. Start by instantiating an AMI (in the right zone?)
  # which serves to create 
  class InitialState < Ami2EbsConversionState
    def enter
      puts "DEBUG: params: #{@context[:ami_id]}, #{@context[:key_name]}, #{@context[:security_group_name]}"
      @context[:instance_id], @context[:dns_name], @context[:availability_zone], 
        @context[:kernel_id], @context[:ramdisk_id], @context[:architecture] =
        launch_instance(@context[:ami_id], @context[:key_name], @context[:security_group_name])
      AmiStarted.new(@context)
    end
  end

  # Ami started. Create a storage
  class AmiStarted < Ami2EbsConversionState
    def enter
      @context[:volume_id] = create_volume(@context[:availability_zone], "10")
      StorageCreated.new(@context)
    end
  end

  # Storage created. Attach it.
  class StorageCreated < Ami2EbsConversionState
    def enter
      attach_volume(@context[:volume_id], @context[:instance_id], @context[:temp_device_name])
      StorageAttached.new(@context)
    end
  end

  # Storage attached. Create a file-system and mount it
  class StorageAttached < Ami2EbsConversionState
    def enter
      @context[:result][:os] =
        connect(@context[:dns_name], @context[:ssh_username],
        @context[:ssh_keyfile], @context[:ssh_keydata],
        @context[:connect_trials], @context[:connect_interval]
      )
      # get root partition label and filesystem type
      @context[:label] = get_root_partition_label()
      @context[:fs_type] = get_root_partition_fs_type()
      create_labeled_fs(@context[:dns_name], @context[:temp_device_name], @context[:fs_type], @context[:label])      
      FileSystemCreated.new(@context)
    end
  end

  # File system created. Mount it.
  class FileSystemCreated < Ami2EbsConversionState
    def enter
      @context[:mount_dir] = "/ebs_#{@context[:volume_id]}"
      mount_fs(@context[:mount_dir], @context[:temp_device_name])
      FileSystemMounted.new(@context)
    end
  end

  # File system created and mounted. Copy the root partition.
  class FileSystemMounted < Ami2EbsConversionState
    def enter
      copy_distribution(@context[:mount_dir])
      CopyDone.new(@context)
    end
  end
  
  # Copy operation done. Unmount volume.
  class CopyDone < Ami2EbsConversionState
    def enter
      unmount_fs(@context[:mount_dir])
      VolumeUnmounted.new(@context)
    end
  end

  # Volume unmounted. Detach it.
  class VolumeUnmounted < Ami2EbsConversionState
    def enter
      detach_volume(@context[:volume_id], @context[:instance_id])
      VolumeDetached.new(@context)
    end
  end

  # VolumeDetached. Create snaphot
  class VolumeDetached < Ami2EbsConversionState
    def enter
      @context[:snapshot_id] = create_snapshot(@context[:volume_id])
      SnapshotCreated.new(@context)
    end
  end

  # Snapshot created. Delete volume.
  class SnapshotCreated < Ami2EbsConversionState
    def enter
      delete_volume(@context[:volume_id])
      VolumeDeleted.new(@context)
    end
  end

  # Volume deleted. Register snapshot.
  class VolumeDeleted < Ami2EbsConversionState
    def enter
      @context[:result][:image_id] = register_snapshot(@context[:snapshot_id], @context[:name],
        @context[:root_device_name], @context[:description], @context[:kernel_id],
        @context[:ramdisk_id], @context[:architecture])
      SnapshotRegistered.new(@context)
    end
  end

  # Snapshot registered. Shutdown instance.
  class SnapshotRegistered < Ami2EbsConversionState
    def enter
      shut_down_instance(@context[:instance_id])
      Done.new(@context)      
    end
  end

  # Instance shutdown. Done.
  class Done < Ami2EbsConversionState
    def done?
      true
    end
  end
  
end

