"""
HueEmulator 1 Helper
"""

import sys, re
from functools import partial
from .Helper import Helper
sys.path.insert(0,"../hue-upnp")
import hueUpnp
from hueUpnp import hue_upnp_super_handler

class pyhue_isy_node_handler(hue_upnp_super_handler):
        def __init__(self, parent, name, node, scene):
                self.parent  = parent
                self.name    = name
                self.node    = node
                self.scene   = scene
                node.status.subscribe('changed', self.get_all_changed)
                super(pyhue_isy_node_handler,self).__init__(name)

        def get_all_changed(self,e):
                self.parent.parent.logger.info('pyhue_isy_node_handler.get_all_changed:  %s e=%s' % (self.name, str(e)));
                self.get_all()

        def get_all(self):
                self.parent.parent.logger.info('pyhue_isy_node_handler.get_all:  %s status=%s' % (self.name, str(self.node.status)));
                # Set all the defaults
                super(pyhue_isy_node_handler,self).get_all()
                # node.status will be 0-255
                self.bri = self.node.status
                if int(self.node.status) == 0:
                        self.on  = "false"
                else:
                        self.on  = "true"
                self.parent.parent.logger.info('pyhue_isy_node_handler.get_all:  %s on=%s bri=%s' % (self.name, self.on, str(self.bri)));
                
        def set_on(self):
                self.parent.parent.logger.info('pyhue_isy_handler.set_on: %s node.on()' % (self.name));
                ret = self.node.on()
                if self.scene != False:
                        self.parent.parent.logger.info('pyhue_isy_handler.set_bri: %s scene.on()' % (self.name));
                        self.scene.on()
                return ret
                
        def set_off(self):
                self.parent.parent.logger.info('pyhue_isy_handler.set_off: %s node.off()' % (self.name));
                ret = self.node.off()
                if self.scene != False:
                        self.parent.parent.logger.info('pyhue_isy_handler.set_bri: %s scene.off()' % (self.name));
                        self.scene.off()
                return ret
                
        def set_bri(self,value):
                self.parent.parent.logger.info('pyhue_isy_handler.set_bri: %s on val=%d' % (self.name, value));
                # Only set directly on the node when it's dimmable and value is not 0 or 254
                if self.node.dimmable and value > 0 and value < 254:
                        self.parent.parent.logger.info('pyhue_isy_handler.set_bri: %s node.on(%d)' % (self.name, value));
                        # val=bri does not work?
                        ret = self.node.on(value)
                else:
                        if value > 0:
                                self.parent.parent.logger.info('pyhue_isy_handler.set_bri: %s node.on()' % (self.name));
                                ret = self.node.on()
                                if self.scene != False:
                                        self.parent.parent.logger.info('pyhue_isy_handler.set_bri: %s scene.on()' % (self.name));
                                        self.scene.on()
                                self.bri = 255
                        else:
                                self.parent.parent.logger.info('pyhue_isy_handler.set_bri: %s node.off()' % (self.name));
                                ret = self.node.off()
                                if self.scene != False:
                                        self.parent.parent.logger.info('pyhue_isy_handler.set_bri: %s scene.off()' % (self.name));
                                        self.scene.off()
                self.parent.parent.logger.info('pyhue_isy_handler.set_bri: %s on=%s bri=%d' % (self.name, self.on, self.bri));
                return ret
                
#class pyhue_isy_var_handler(hue_upnp_super_handler):
#        def __init__(self, parent, name, var):
#                self.parent  = parent
#                self.name    = name
#                self.var     = var
#                self.update()
#                #node.subscribe('changed', partial(self.update))
#                self.handler = var.val.subscribe('changed', partial(self.update))
#                super(isy_rest_handler,self).__init__(name)
#
#        def update(self):
#                # TODO: if var.on is true?
#                if self.var.val == 0:
#                        self.on  = "false"
#                        self.bri = 0
#                else:
#                        self.on  = "true"
#                        self.bri = self.var.val
#                self.xy  = [0.0,0.0];
#                self.ct  = 0
#                
#        def set(self,data):
#                ret = False
#                self.parent.parent.logger.info('pyhue_var_handler.set:  ' + str(data));
#                if 'bri' in data:
#                        bri = str(data['bri'])
#                        self.parent.parent.logger.info('pyhue_isy_handler.set: on val=' + bri);
#                        # val=bri does not work?
#                        ret = self.var.val(bri)
#                        if ret:
#                                self.on = "true"
#                                self.bri = bri
#                elif 'on' in data:
#                        if data['on']:
#                                ret = self.var.val(1)
#                                if ret:
#                                        self.on = "true"
#                        else:
#                                ret = self.var.val(0)
#                                if ret:
#                                        self.on = "false"
#                return ret
                
 
#class pyhue_maker_handler(object):
#    def __init__(self, parent, on_event, off_event):
#        self.parent    = parent
#        self.on_event  = on_event
#        self.off_event = off_event
#        
#    def on(self):
#        self.parent.parent.logger.info('device_maker_on:  ' + self.on_event);
#        return self.parent.post_ifttt_maker(self.on_event)
# 
#    def off(self):
#        self.parent.parent.logger.info('device_maker_off: ' + self.off_event);
#        return self.parent.post_ifttt_maker(self.off_event)
 
class PyHue(Helper):

    def __init__(self,parent,hconfig):
        self.optional = { 'devices' : { 'default' : [] }, 'use_spoken' : { 'default' : 'true'} }
        self.pdevices  = []
        self.lpfx = 'pyhue:'
        super(PyHue, self).__init__(parent,hconfig)
        
    # Schedule the emulator to start immediatly
    def sched(self):
        super(PyHue, self).sched()
        
    # Initialize all on startup
    def start(self):
        super(PyHue, self).start()
        errors = 0
        for device in self.pdevices:
            try:
                self.add_device(device)
            except ValueError as e:
                self.parent.logger.error(str(e))
                errors += 1
        lpfx = self.lpfx + ':auto_add_isy:'
        for child in self.parent.isy.nodes.allLowerNodes:
            if child[0] is 'node':
                mnode = self.parent.isy.nodes[child[2]]
                spoken = mnode.spoken
                if spoken is not None:
                    # TODO: Should this be a comman seperate list of which echo will respond?
                    # TODO: Or should that be part of notes?
                    if spoken == '1':
                        spoken = mnode.name
                    self.parent.logger.info(lpfx + " name=" + mnode.name + ", spoken=" + str(spoken))
                    # Is it a controller of a scene?
                    cgroup = mnode.get_groups(responder=False)
                    if len(cgroup) > 0:
                        cnode = self.parent.isy.nodes[cgroup[0]]
                        self.parent.logger.info(lpfx + " is a scene controller of " + str(cgroup[0]) + '=' + str(cnode) + ' "' + cnode.name + '"')
                    else:
                        cnode = False
                    self.pdevices.append(pyhue_isy_node_handler(self,spoken,mnode,cnode))
        for var in self.parent.isy.variables.children:
                # var is a tuple of type, name, number
                # TODO: Use ([^\/]+) instead of (.*) ?
                match_obj = re.match( r'.*\.Spoken\.(.*)', var[1], re.I)
                if match_obj:
                        var_obj = self.parent.isy.variables[var[0]][var[2]]
                        self.pdevices.append(pyhue_isy_var_handler(self,match_obj.group(1),var))
        #errors += 1
        if errors > 0:
            raise ValueError("See Log")
        self.parent.sched.add_job(partial(hueUpnp.run,self.pdevices,self.parent.logger))

    def add_device(self,config):
        self.parent.logger.info(self.lpfx + ' ' + str(config))
        if not 'name' in config:
            raise ValueError("No name defined for " + str(config))
        if not 'type' in config:
            config['type'] = 'ISY'
        if config['type'] == 'ISY':
            #node = self.parent.isy.nodes['Family Room Table']
            dname = config['name']
            if 'address' in config:
                dname = str(config['address'])
            try:
                node = self.parent.isy.nodes[dname]
            except:
                node = self.get_isy_node_by_basename(dname)
            if node is None:
                raise ValueError("Unknown device name or address '" + dname + "'")
            else:
                self.pdevices.append([ config['name'], device_isy_onoff(self,node)])
        elif config['type'] == 'Maker':
            #if self.config in 'ifttt':
            #    if not self.config['ifttt'] in 'maker_secret_key':
            #        raise ValueError("Missing maker_secret_key in ifttt from config file")
            #else:
            #    raise ValueError("Missing ifttt with maker_secret_key in config file")

            self.pdevices.append([ config['name'], device_maker_onoff(self,config['on_event'],config['off_event'])])
                
        else:
            raise ValueError("Unknown PyHue device type " + config['type'])