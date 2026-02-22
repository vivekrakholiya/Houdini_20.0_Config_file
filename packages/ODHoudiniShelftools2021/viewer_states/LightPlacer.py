from __future__ import print_function

from stateutils import ancestorObject
import viewerstate.utils as util
import hou, tempfile, os

class MyState(object):
    def __init__(self, state_name, scene_viewer):
        self.state_name    = state_name
        self.scene_viewer  = scene_viewer

        self.projMode      = "ref"
        self.incMode       = "0.1"
        self.wheelMode     = "Offset"
        self.adjustMode    = "0"
        self._geometry     = None
        self.guide_geo1    = hou.Geometry()
        # self.colorAttrib   = self.guide_geo1.addAttrib(hou.attribType.Prim, "Cd", (0.0, 1.0, 0.0))
        self.corner_text_drawable = None

        line_verb          = hou.sopNodeTypeCategory().nodeVerb("line")
        line_verb.setParms({"origin": hou.Vector3(0,0,0), "dir": hou.Vector3(0,1,0), "dist": 1})
        line_verb.execute(self.guide_geo1, [])


        color_attrib = self.guide_geo1.addAttrib(hou.attribType.Prim, "Cd", (1.0, 1.0, 1.0))
        alpha_attrib = self.guide_geo1.addAttrib(hou.attribType.Prim, "Alpha", 1.0)
        for prim in self.guide_geo1.prims():
            prim.setAttribValue(color_attrib, hou.Color(0.2, 1.0, 0.2).rgb())
            prim.setAttribValue(alpha_attrib, 1.0)

        if hou.applicationVersion()[0] > 17:
          self.drawable1     = hou.SimpleDrawable(self.scene_viewer, self.guide_geo1, "guide_1")
          self.corner_text_drawable = hou.TextDrawable(self.scene_viewer, "corner_text_drawable")
        else:
          self.drawable1     = hou.Drawable(self.scene_viewer, self.guide_geo1, "guide_1")

        self.drawable1.enable(True)
        self.drawable1.show(True)

        (x,y,width,height) = self.scene_viewer.curViewport().size()
        margin = 10

        if self.corner_text_drawable:
            self.corner_text_drawable.setParams({
                "text": "",
                'color1' : (1.0,1.0,1.0, 1.0),
                'color2' : (0.0,0.0,0.0, 1.0),
                'translate' : hou.Vector3(0, height, 0),
                'origin' : hou.drawableTextOrigin.UpperLeft,
                'margins': hou.Vector2(margin, -margin),
                'highlight_mode': hou.drawableHighlightMode.MatteOverGlow,
                "glow_width": 1.0,
            })
            self.corner_text_drawable.show(True)

        self.startpos      = hou.Vector3(0,0,0)
        self.endpos        = hou.Vector3(0,0,0)
        self.drawdirection = hou.Vector3(0,1,0)
        self.norm          = hou.Vector3(0,1,0)
        self.lastRayOrig   = hou.Vector3(0,0,0)
        self.lastRayDir    = hou.Vector3(0,0,0)
        self.scroll        = 0
        self.scrollindicator = 0
        self.scale         = 1.0
        self.angle         = 0.0

        # selected geometry
        #self.selectedGeometry = self.getSelectedGeometry()
        network = ancestorObject(scene_viewer.pwd())
        self.selectedGeometry = network.displayNode().geometry()
        self.scene_viewer.setPromptMessage("Click/Drag over Object to Place Lights")

    def createGuideTransform(self, a_position, a_direction, a_scale):
        # translation
        trans = hou.hmath.buildTranslate(a_position)
        # rotation
        rot = hou.Vector3(0,1,0).matrixToRotateTo(a_direction) 
        if a_direction.dot(hou.Vector3(0,1,0)) <= -0.9999:
            rot = hou.hmath.buildRotateAboutAxis(hou.Vector3(1,0,0), 180)
        # scale
        scale = hou.hmath.buildScale(a_scale, a_scale, a_scale)
        # combine
        xform = rot.__mul__(scale)
        xform = xform.__mul__(trans)
        return xform

    def set_corner_text(self):
        label = "<font color=green>ON</font>"
        text = "<b><font face='Source Code Pro' size=4>Trace/Placement mode: " + label + "</font></b>"
        self.corner_text_drawable.setParams({
            "text": text
        })
        self.scene_viewer.curViewport().draw()

    def onDraw( self, kwargs ):
        """ This callback is used for rendering the drawables
        """
        handle = kwargs["draw_handle"]
        self.corner_text_drawable.draw(handle)


    def onGenerate(self, kwargs):
        # Show a prompt to the user
        self.scene_viewer.setPromptMessage("Click/Drag over Object to Place Lights")

    def onEnter(self, kwargs):
        print("entered")

        self.set_corner_text()

        pass
        #node = kwargs["node"]
        #if inputs and inputs[0]:
        #    self._geometry = inputs[0].geometry()

    def getSelectedGeometry(self):
        SelectedNodes = hou.selectedNodes()
        if len(SelectedNodes) > 0:
            return SelectedNodes[0].geometry()
        else:
            return None
    
    def setLightTransform(self, node, startpos, normal, ray_orig, ray_dir, scale, option):
        if self.projMode == "dif":
            endpos = startpos + normal * (1.0+self.scroll*float(self.incMode))
            direction = hou.Vector3(endpos - startpos).normalized()
            self.drawdirection = hou.Vector3(endpos - startpos).normalized()

        if self.projMode == "ref":
            r = ray_dir - 2 * normal * (ray_dir.dot(normal))
            direction = r.normalized()
            endpos = startpos + direction * (1.0+self.scroll*float(self.incMode))
            self.drawdirection = direction

        # if self.projMode == "rim":
        #     r = ray_dir
        #     #r = r.cross(normal)
        #     #r = a.cross(normal)
        #     direction = r.normalized()
        #     endpos = startpos + direction * (1.0+self.scroll*float(self.incMode))
        #     self.drawdirection = direction

        lines = None
        if os.path.exists(tempfile.gettempdir() + os.sep + "odlsel.txt"):
            f = open(tempfile.gettempdir() + os.sep + "odlsel.txt", "r")
            lines = f.readlines()
            f.close()

        if lines:
            node = hou.node(lines[0].strip())
        else:
            node = None

        if node:
            if option == 0:
                #sx = self.scale#node.parm("sx").eval()# + self.scale
                #sy = self.scale#node.parm("sy").eval()# + self.scale
                #sz = self.scale#node.parm("sz").eval()# + self.scale
                if node.parm("areasize1"):
                    sx = node.parm("areasize1").eval() + self.scrollindicator * 0.1# + self.scale
                    sy = sx
                    sz = sx

                    if node.parm("areasize2"):
                        sy = node.parm("areasize2").eval() + self.scrollindicator * 0.1# + self.scale
                    if node.parm("areasize3"):
                        sz = node.parm("areasize3").eval() + self.scrollindicator * 0.1# + self.scale               

                    #hou.node("/obj/hlight1").setPreTransform(xform)
                    node.setParmTransform(self.createGuideTransform(endpos, direction, 1.0+self.scroll*float(self.incMode)))

                    if node.parm("areasize1"):
                        node.parm("areasize1").set(sx)
                    if node.parm("areasize2"):
                        node.parm("areasize2").set(sy)
                    if node.parm("areasize3"):
                        node.parm("areasize3").set(sz)
                    node.setParms({"rx": node.parm("rx").eval()-90})   

                elif node.parm("ar_quad_sizex"):
                    sx = node.parm("ar_quad_sizex").eval() + self.scrollindicator * 0.1# + self.scale
                    sy = sx
                    sz = sx
                    if node.parm("ar_quad_sizey"):
                        sy = node.parm("ar_quad_sizey").eval() + self.scrollindicator * 0.1# + self.scale

                    #hou.node("/obj/hlight1").setPreTransform(xform)
                    node.setParmTransform(self.createGuideTransform(endpos, direction, 1.0+self.scroll*float(self.incMode)))

                    if node.parm("ar_quad_sizex"):
                        node.parm("ar_quad_sizex").set(sx)
                    if node.parm("ar_quad_sizey"):
                        node.parm("ar_quad_sizey").set(sy)

                    node.setParms({"rx": node.parm("rx").eval()-90})   
                else:
                    sx = node.parm("sx").eval() + self.scrollindicator * 0.1# + self.scale
                    sy = node.parm("sy").eval() + self.scrollindicator * 0.1# + self.scale
                    sz = node.parm("sz").eval() + self.scrollindicator * 0.1# + self.scale               
                    #hou.node("/obj/hlight1").setPreTransform(xform)
                    node.setParmTransform(self.createGuideTransform(endpos, direction, 1.0+self.scroll*float(self.incMode)))
                    node.setParms({"sx": sx, "sy": sy, "sz": sz, "rx": node.parm("rx").eval()-90})
            else:
                xform = node.worldTransform()
                rot = hou.hmath.buildRotate(0,0,self.angle)
                node.setWorldTransform(xform.preMult(rot))

            self.drawable1.setTransform(self.createGuideTransform(startpos, direction, 1.0+self.scroll*float(self.incMode)))
            


    def onMouseEvent(self, kwargs):
        #node = kwargs["node"]
        ui_event = kwargs["ui_event"]
        
        ray_origin, ray_dir = ui_event.ray()

        dev = ui_event.device()

        # no geometry selected, so no measurement
        if not self.selectedGeometry: 
            return

        if self.selectedGeometry:

            gi = util.GeometryIntersector(self.selectedGeometry, scene_viewer = self.scene_viewer)
            gi.intersect(ray_origin, ray_dir)

            intersected = gi.prim_num != -1
            hit = intersected
            pos = gi.position
            hitnormal = gi.normal

            #hit, pos, norm, uvw = util.sopGeometryIntersection(self.selectedGeometry, ray_origin, ray_dir)
            if hit != -1:
                if dev.isLeftButton():
                    self.norm = hitnormal
                    self.startpos = pos

                    lines = None
                    if os.path.exists(tempfile.gettempdir() + os.sep + "odlorig.txt"):
                        f = open(tempfile.gettempdir() + os.sep + "odlorig.txt", "r")
                        lines = f.readlines()
                        f.close()
                    if hou.node(lines[0].strip()):
                        self.selectedGeometry = hou.node(lines[0].strip()).geometry()

                    #find parent
                    parent = self.selectedGeometry.sopNode().parent()
                    # Use the container's transform to display the cursor in world space
                    parent_xform = parent.worldTransform()
                    self.startpos *= parent_xform
                    # Build a Matrix4 from the world space translate
                    #m = hou.hmath.buildTranslate(world_pos)
                    #print ("startpos", self.startpos, "hitnormal", self.norm)
                    #ray_dir = hou.Vector3(self.startpos - ray_origin).normalized()

                    self.lastRayOrig = ray_origin
                    self.lastRayDir = ray_dir
                    self.scale = 1
                    self.scrollindicator = 0
                    self.setLightTransform(None, self.startpos, self.norm, ray_origin, ray_dir, self.scale, 0)

    def onMouseWheelEvent(self, kwargs):
        # Get the UI device object
        device = kwargs["ui_event"].device()
        scroll = device.mouseWheel()
        if self.wheelMode == "Offset" and not device.isCtrlKey() and not device.isShiftKey():
            self.scroll += scroll
        self.drawable1.setTransform(self.createGuideTransform(self.startpos, self.drawdirection, 1.0+self.scroll*float(self.incMode)))
        self.endpos = self.startpos + self.norm * (1.0+self.scroll*float(self.incMode))

        if self.wheelMode == "Scale" or device.isCtrlKey():
            #print ("adjusting scale", self.scale)
            #self.scale += scroll * 0.1;
            self.scale = 1;
            self.scrollindicator = scroll

        if not device.isCtrlKey():
            self.scrollindicator = 0

        if self.wheelMode == "Rotation" or device.isShiftKey():
            #print ("adjusting rotation", self.scale)
            self.angle = scroll*3

        if self.wheelMode == "Rotation" or device.isShiftKey():
            self.setLightTransform(None, self.startpos, self.norm, self.lastRayOrig, self.lastRayDir, self.scale, 1)
        else:
            self.setLightTransform(None, self.startpos, self.norm, self.lastRayOrig, self.lastRayDir, self.scale, 0)

    # the menu callback
    def onMenuAction(self, kwargs):
        action = kwargs["menu_item"]
        if action == 'mode':
            self.projMode = kwargs["mode"]
        if action == 'inc':
            self.incMode = kwargs["inc"]
        if action == 'rot':
            self.wheelMode = kwargs["rot"]  
        if action == 'adj':
            self.adjustMode = kwargs["adj"]            

    def onExit(self, kwargs):
        #self.scene_viewer.setGroupListVisible(False)
        self.scene_viewer.clearPromptMessage()

def createViewerStateTemplate():
    # Choose a name and label 
    state_name = "ODLightPlacer"
    state_label = "OD Light Placer"
    category = hou.sopNodeTypeCategory()

    # Create the template
    template = hou.ViewerStateTemplate(state_name, state_label, category)
    template.bindFactory(MyState)

    # Other optional bindings will go here...
    menu = hou.ViewerStateMenu("projMode", "projMode")
    menu.addRadioStrip("mode", "Projection Mode", "ref")
    menu.addRadioStripItem("mode", "dif", "Diffuse")
    menu.addRadioStripItem("mode", "ref", "Reflection")
    # menu.addRadioStripItem("mode", "rim", "Rim")

    menu.addRadioStrip("inc", "Scroll Wheel Multiplier", "0.1")
    menu.addRadioStripItem("inc", "0.01", "0.01")
    menu.addRadioStripItem("inc", "0.1", "0.1")
    menu.addRadioStripItem("inc", "1", "1")
    menu.addRadioStripItem("inc", "10", "10")

    menu.addRadioStrip("rot", "Scroll Wheel Mode", "Offset")
    menu.addRadioStripItem("rot", "Offset", "Offset")
    menu.addRadioStripItem("rot", "Rotation", "Rotation (shift key)")
    menu.addRadioStripItem("rot", "Scale", "Scale (ctrl key)")

    # menu.addRadioStrip("adj", "Light Change", "0")
    # menu.addRadioStripItem("adj", "0", "Position & Rotation")
    # menu.addRadioStripItem("adj", "1", "Position Only")    
    # menu.addRadioStripItem("adj", "2", "Rotation Only")    

    template.bindMenu(menu)

    # returns the 'mystate' template
    return template
