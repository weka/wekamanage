


Take the ISO and install it on a VM on KVM/Rocky Virt.

Shutdown the VM
Note the qcow2 filename
Copy .qcow2 file here (~9GB)
Convert it with the provided script to .vhdx with provided script.   (from, to filenames needed)
Upload to aws bucket
edit the containers.json to reflect the new .vhdx filename
run 'import_ami'

Note the job number and monitor with the monitor command (give job #)

Note final AMI name from monitoring
oYou should be able to find it here: https://us-west-2.console.aws.amazon.com/ec2/home?region=us-west-2#Images:visibility=owned-by-me
