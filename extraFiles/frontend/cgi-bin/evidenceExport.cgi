#!/bin/sh
echo Content-type: text/html
echo ""

source defs.cgi

if grep -q "1" $FABRIC/$DEF_IQN/tpgt_1/enable ; then 
rm -r $FABRIC/$DEF_IQN/tpgt_1/lun/lun_0
rm -r $FABRIC/$DEF_IQN/tpgt_1/np/192.168.0.1:3260
rm -r $FABRIC/$DEF_IQN/tpgt_1
rm -r $TARGET/iblock_0/lvm_test0
rm -r $TARGET/iblock_0
echo "done"
else
	if ls -la /sys/block | grep ata. | grep host0 | grep -qo sd.
	then
		#create a IBLOCK HBA and virtual storage object
		mkdir -p $TARGET/iblock_0/lvm_test0
		# Tell the virtual storage object what struct block_device we want
		echo "udev_path=/dev/$EV_DISK" > $TARGET/iblock_0/lvm_test0/control
		echo "readonly=1" > $TARGET/iblock_0/lvm_test0/control
		# Enable the virtual storage object and call bd_claim()
		echo 1 > $TARGET/iblock_0/lvm_test0/enable

		#create the network portal on $DEF_IQN/tpgt_1
		mkdir -p "$FABRIC/$DEF_IQN/tpgt_1/np/192.168.0.1:3260"
		# Create LUN 0 on $DEF_IQN/tpgt_1
		mkdir -p "$FABRIC/$DEF_IQN/tpgt_1/lun/lun_0"
		# Create the iSCSI Target Port Mapping for $DEF_IN/tpgt_1 LUN 0
		# to lvm_test0 and give it the port symbolic name of lio_west_port
		ln -s $TARGET/iblock_0/lvm_test0 "$FABRIC/$DEF_IQN/tpgt_1/lun/lun_0/lio_west_port"

		# Allow iSCSI Initiators to login to $DEF_IQN/tpgt_1
		#warning Currently uses generate_node_acls=1,cache_dynamic_acls=1,demo_mode_lun_access=1
		echo 1 > $FABRIC/$DEF_IQN/tpgt_1/enable
		#this is needed or else the target will require the initiators iqn
		echo 0 > $FABRIC/$DEF_IQN/tpgt_1/attrib/authentication
		echo 1 > $FABRIC/$DEF_IQN/tpgt_1/attrib/cache_dynamic_acls
		echo 1 > $FABRIC/$DEF_IQN/tpgt_1/attrib/generate_node_acls
		echo "done"
	else
		echo "Evidence drive not found"
	fi
fi
