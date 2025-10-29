
from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.button import MDRaisedButton
from kivy.uix.screenmanager import ScreenManager, Screen
import socket
import threading
from kivy.uix.label import Label
from kivy.clock import mainthread

import shutil



from struct import pack
from construct import *
from kivy.uix.floatlayout import FloatLayout


    
from kivy.uix.image import Image
from kivymd.uix.filemanager import MDFileManager
import requests

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.toast import toast
from kivymd.uix.floatlayout import MDFloatLayout
import os
from kivymd.uix.textfield import MDTextField

from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.button import MDFlatButton
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.button import MDIconButton
from kivy.clock import Clock
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.button import MDFlatButton


GMA_VERSION = b"\x03".decode("utf-8")

GMAFile = "all_file_meta" / Struct(
    "file_number" / Int32ul,
    "data"
    / IfThenElse(
        this.file_number != 0,
        "data"
        / Struct(
            "file_name" / CString("utf8"), "file_size" / Int64sl, "file_crc" / Int32ul
        ),
        Pass,
    ),
)



class FileContents(Adapter):
    def _encode(self, obj, context, path):
        return b"".join(obj)

    def _decode(self, obj, context, path):
        contents = []
        begin = 0
        for filemeta in context._.all_file_meta:
           
            if filemeta.file_number == 0:
                break

            size = filemeta.data.file_size
            contents.append(obj[begin : begin + size])
            begin += size

        return contents
        
        
def file_content_size(context):
    total = 0
    for filemeta in context.all_file_meta:
        if filemeta.file_number == 0:
            return total

        total += filemeta.data.file_size





        
         
         
         
         
         
         
         
         
        


       


GMAContents = "content" / Struct(
    "signature" / Const(b"GMAD"),
    "format_version" / PaddedString(1, "utf8"),
    "steamid" / Int64sl,
    "timestamp" / Int64sl,
    "required_content" / CString("utf8"),
    "addon_name" / CString("utf8"),
    "addon_description" / CString("utf8"),
    "addon_author" / CString("utf8"),
    "addon_version" / Int32sl,
   
    "all_file_meta" / RepeatUntil(lambda x, lst, ctx: x["file_number"] == 0, GMAFile),
    "total_file_size" / Computed(lambda ctx: file_content_size(ctx)),
    "embedded_files"
    / LazyStruct("contents" / FileContents(Bytes(this._.total_file_size))),
)

GMAVerifiedContents = "GMAVerifiedContents" / Struct(
    GMAContents,
    "addon_crc" / Optional(Int32ul),
    "MagicValue" / Optional(Int8ul)
 
)

GMAVerifiedContents = "GMAVerifiedContents" / Struct(
    GMAContents,
    "addon_crc" / Optional(Int32ul),
    "MagicValue" / Optional(Int8ul)
  
)














class MainApp(MDApp):
    def build(self):
        
        
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.accent_palette = "Orange"
    
        
        
        
        
        
        
        
        
        self.layout = MDFloatLayout()
        path = os.path.expanduser("/sdcard")  
        self.file_manager = MDFileManager(
        exit_manager=self.exit_manager, 
        select_path=self.on_select,
        background_color_toolbar="brown",
        background_color_selection_button="brown",
       icon_color="brown"
           

        

        
        
        )


        
        
       
        bg_im= Image(source='pic1.png', size_hint=(3, 1.3),pos_hint={'center_x': 0.5, 'center_y': 0.5})
                         
                         
                         
        self.layout.add_widget(bg_im)
        
        
        self.text_input=MDTextField(hint_text="Path To The .GMA File.", pos_hint={'center_x': 0.35, 'center_y': 0.80},mode='round', helper_text='Ex : /sdcard/yourfile.gma', helper_text_mode="on_focus",size=(600, 600), size_hint_min=(None, None), size_hint_max=(490,490))
        self.layout.add_widget(self.text_input)
        button = MDRoundFlatButton(text='Extract',pos_hint={'center_x': 0.80, 'center_y': 0.80},text_color='black', md_bg_color='white')
        button.bind(on_press=self.on_clickk)
        self.labell=MDLabel(text="OR", pos_hint={'center_x': 0.969, 'center_y': 0.30},theme_text_color='Custom', text_color=(1,1,1,1))
        self.text_inputt=MDTextField(hint_text="Mod Link (Only Steam)", pos_hint={'center_x': 0.35, 'center_y': 0.70},mode='round', helper_text='Ex : https://steamcommunity.com/...', helper_text_mode="on_focus",size=(600, 600), size_hint_min=(None, None), size_hint_max=(490,490))
        buttonn = MDRoundFlatButton(text='Submit',pos_hint={'center_x': 0.80, 'center_y': 0.70},text_color='black', md_bg_color='white')
        buttonn.bind(on_press=self.on_clickkk)
        self.layout.add_widget(buttonn)
        self.layout.add_widget(self.text_inputt)
        self.layout.add_widget(self.labell)
        
        button3 = MDFlatButton(text='Info',pos_hint={'center_x': 0.93, 'center_y': 0.98}, theme_text_color="Custom",text_color='white')
        button3.bind(on_press=self.notif_on)
        self.layout.add_widget(button3)
        button4 = MDFlatButton(text='Errors',pos_hint={'center_x': 0.10, 'center_y': 0.98}, theme_text_color="Custom",text_color='white')
        button4.bind(on_press=self.notiff_onn)
        buttonp = MDRoundFlatButton(text='Choose From Files',pos_hint={'center_x': 0.5, 'center_y': 0.60},text_color='black', size_hint= (.9, .01), md_bg_color='white')
        button333 = MDRoundFlatButton(text='Download Addons',pos_hint={'center_x': 0.5, 'center_y': 0.20},text_color='black', size_hint= (.9, .01), md_bg_color='white', on_press=self.switch_to_third)
        self.kol4 = MDRoundFlatButton(text='Download',pos_hint={'center_x': 0.5, 'center_y': 0.70},text_color='black', size_hint= (.9, .01), md_bg_color='white', on_press=self.switch_to_third)
        buttonp.bind(on_release=self.show_file_manager)
        labe=MDLabel(text="OR", pos_hint={'center_x': 1.28, 'center_y': 0.75},theme_text_color='Custom', text_color=(1,1,1,1))
        self.layout.add_widget(labe)
        self.layout.add_widget(button4)
        self.layout.add_widget(buttonp)
        self.layout.add_widget(button333)
       
       
        
        
        
        self.layout.add_widget(button)
        self.label = MDLabel(size=(600, 600), size_hint_min=(None, None), size_hint_max=(1200,1000))
        
        self.layout.add_widget(self.label)
       
        
        self.layout2 = FloatLayout()
        path = os.path.expanduser("/sdcard")  
        self.file_manager = MDFileManager(
        exit_manager=self.exit_manager, 
        select_path=self.on_select,
        background_color_toolbar="brown",
        background_color_selection_button="brown",
       icon_color="brown"
       
           

  
        
        )


        
        bg_im= Image(source='yourpic2.png', size_hint=(3, 1.3),pos_hint={'center_x': 0.5, 'center_y': 0.5})
        
        
        self.button_second_to_main = MDIconButton(icon="arrow-left",pos_hint={'center_x': 0.90, 'center_y': 0.95},theme_text_color='Custom',text_color='black',md_bg_color='white',on_press=self.switch_to_main_layout
            
            
            
        )
        buttonp2 = MDRoundFlatButton(text='Choose From Files',pos_hint={'center_x': 0.5, 'center_y': 0.20},text_color='black', size_hint= (.9, .01), md_bg_color='white')
        buttonp2.bind(on_release=self.show_file_manager)
        
        self.text_input2=MDTextField(hint_text="Path To The .VPK File.", pos_hint={'center_x': 0.35, 'center_y': 0.80},mode='round', helper_text='Ex : /sdcard/yourfile.vpk', helper_text_mode="on_focus",size=(600, 600), size_hint_min=(None, None), size_hint_max=(480,480))
        self.button22 = MDRoundFlatButton(text='Extract',pos_hint={'center_x': 0.80, 'center_y': 0.80},text_color='black', md_bg_color='white')
        self.button22.bind(on_press=self.on_clickkkk)
        self.labell=MDLabel(text="OR", pos_hint={'center_x': 0.969, 'center_y': 0.30},theme_text_color='Custom', text_color=(1,1,1,1))
        self.labelkl=MDLabel(text="OR", pos_hint={'center_x': 0.969, 'center_y': 0.150},theme_text_color='Custom', text_color=(1,1,1,1))
        self.layout.add_widget(self.labelkl)
       
        
        
        self.label22 = MDLabel(size=(600, 600), size_hint_min=(None, None), size_hint_max=(1200,1000))
        
        
        
                         
                
                         
        self.layout2.add_widget(bg_im)
        self.layout2.add_widget(self.button_second_to_main)
        self.layout2.add_widget(buttonp2)      
        self.layout2.add_widget(self.text_input2)
        self.layout2.add_widget(self.button22)
        self.layout2.add_widget(self.label22)
        self.layout3=MDFloatLayout()
  
        
                
        
        
        
        
        
        
        
        self.screen_manager = ScreenManager()

        self.main_screen = Screen(name="main")
        self.second_screen = Screen(name="second")
        self.third_screen = Screen(name="third")
        
        bg_im3= Image(source='yourpic3.png', size_hint=(3, 1.3),pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.layout3.add_widget(bg_im3)
        self.kol2 = MDRoundFlatButton(text="Check",pos_hint={'center_x': 0.80, 'center_y': 0.80},text_color='black', md_bg_color='white', on_press=self.on_down)
        self.kol3=MDTextField(hint_text="Addon Link", pos_hint={'center_x': 0.35, 'center_y': 0.80},mode='round', helper_text='Ex : https://steam...', helper_text_mode="on_focus",size=(600, 600), size_hint_min=(None, None), size_hint_max=(490,490))
        
        self.kol1 = MDIconButton(icon="arrow-left",pos_hint={'center_x': 0.90, 'center_y': 0.95},theme_text_color='Custom',text_color='black',md_bg_color='white',on_press=self.switch_to_main_layout)
        self.layout3.add_widget(self.kol1)
        self.layout3.add_widget(self.kol2)
        self.layout3.add_widget(self.kol3)
        self.layout3.add_widget(self.kol4)
        
        "bandor"
        
        
        
        self.third_screen.add_widget(self.layout3)
        
        
        
        
        
        
        
        
        
        

        self.button_main_to_second = MDRoundFlatButton(text='Extract VPK Files',pos_hint={'center_x': 0.5, 'center_y': 0.10},text_color='black', size_hint= (.9, .01), md_bg_color='white',on_press=self.switch_to_second_layout)
        
        
        

        self.layoutt = MDFloatLayout()
        button = MDFlatButton(text='to', pos_hint=({'center_x':0.20, 'center_y':0.30}))
        self.layoutt.add_widget(button)
        
        self.main_screen.add_widget(self.layout)
        self.main_screen.add_widget(self.button_main_to_second)
        
        
        
        self.second_screen.add_widget(self.layout2)
        

        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.second_screen)
        self.screen_manager.add_widget(self.third_screen) 
        

        return self.screen_manager
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
  
        
    def notif_on(self, instance):
         dialog = MDDialog(title="GmadExtractor", text="Created By : boo271\nHow To Use : \n1. give access files permission to the app.\n2. put the right directory to your gmad file.\n3. if the file's big, the app will be stuck for some time, because its compressing it, just wait until the process complete.\nDiscord : https://discord.com/invite/CktPBBGfVR")
         dialog.open()
         
         
    def notiff_onn(self, instance):
         dialog = MDDialog(title="Gmad Errors", text="-if you got  'this is not a gmad file' error, this means that you are probably trying to extract an LZMA or BIN file, make sure to open this file that you tried to extract view the content with ZArchiver, then extract it and rename it to .gma.\n-Connection Error : that means the link is not valid, or check your internet\nif you got any other Error, Dm on Discord : boo271, Read Info to join the Discord Server.")
         dialog.open()
    def show_file_manager(self, instance):
        self.file_manager.show('/sdcard') 
        
    def on_clickkk(self, instance):
        
        
        self.label.pos_hint=({'center_x': 0.60, 'center_y': 0.90})
        self.label.color=(1,1,1,1)
        self.label.text=""
  
        self.show_dialog22()
        Clock.schedule_once(self.on_submit, 2)
    @mainthread
    def show_dialog(self):
        self.dialog = MDDialog(
            title='Extracting...',
            type="custom",
            auto_dismiss=False,
            content_cls=MDSpinner(size_hint=(None, None), size=(46, 46), active=True)
        )
        self.dialog.open()
    @mainthread
    def show_dialog22(self):
        self.dialog = MDDialog(
            title='Downloading...',
            type="custom",
            auto_dismiss=False,
            content_cls=MDSpinner(size_hint=(None, None), size=(46, 46), active=True)
        )
        self.dialog.open()
        
        
        
    @mainthread
    def show_dialogg(self, title, text):
        self.dialog = MDDialog(
            title=title,
            text = text,
            auto_dismiss=True,)
        
                   
                          
                          
            
            
        self.dialog.open()
        
        
        

    def on_select(self, path: str):
     
     
     
     
     
        
        self.exit_manager()
        toast(path)
        
        self.text_input.text=str(path)
        self.text_input2.text=str(path)

    def exit_manager(self, *args):
        self.file_manager.close()
        
        
    def on_down(self, instance):
        
        
        self.label.pos_hint=({'center_x': 0.60, 'center_y': 0.90})
        self.label.color=(1,1,1,1)
        self.label.text=""
    
    	
        Clock.schedule_once(self.on_wow, 2)   
        self.show_dialog()
    def on_wow(self, instance):
    	try:
    		word=self.kol3.text
    		
    		sss = requests.post('https://ytshorts.savetube.me/api/v1/steam-workshop-downloader', data={'url': word})
    		if sss.status_code == 200:
    			woow = sss.json()
    			de = woow['response']
    			if de[0]['file_url']=='':
    				self.dialog_dismisss()
    				self.show_dialogg("SWD", "Status : Not Available in SWD.\nMod Info : \n" 'Creator : '+(str(de[0]['creator']))+'\n'+'Created : '+(str(de[0]['time_created']))+'\n'+'Size : '+(str(de[0]['file_size']))+'\n'+'Updated : '+(str(de[0]['time_updated']))+'\n'+'Download Link : ' + 'unavailable in SWD')
    		
    		
    	
    	
    	
    		
    		
    	
    			
    			return
    		self.dialog_dismisss()
    		self.show_dialogg(de[0]['title'], 'Creator : '+(str(de[0]['creator']))+'\n'+'Created : '+(str(de[0]['time_created']))+'\n'+'Size : '+(str(de[0]['file_size']))+'\n'+'Updated : '+(str(de[0]['time_updated']))+'\n'+'Download Link : ' + 'unavailable in SWD')
    	except Exception as fe:
    		self.dialog.dismisss()
    		self.show_dialogg('SWD', str(fe))

    		    		
    	
		
    	
    	    		
		
		
		
	
    	
		
    	
    		
    	    		
    	
    		
    				
    			
    			
    	
    			
    			
    	
		
			
    	
    		
    				
    	
		
	
		
		
	
			
			
		
		
		
		
		
			
		
			
		
		
		
		
		
		
		
		
			
	
	
    	
    	
    
    
    
    def on_clickk(self, instance):
        
        
        self.label.pos_hint=({'center_x': 0.60, 'center_y': 0.90})
        self.label.color=(1,1,1,1)
        self.label.text=""
        self.show_dialog()
    	
        Clock.schedule_once(self.on_button_press, 2)
        
    def on_clickkkk(self, instance):
        
        
        self.label22.pos_hint=({'center_x': 0.60, 'center_y': 0.88})
        self.label22.color=(1,1,1,1)
        self.label22.text=""
        Clock.schedule_once(self.extract_vpk, 2)
        self.show_dialog()    
        
        
    def extract_vpk(self,instance):
    	valuee = self.text_input2.text
    	if valuee=="":
    		valuee = "Kss.jska.aj"
    		
    	woww = valuee.split('.')[-2]
    	
    	
    	try:
    		
    		
    		shutil.rmtree('/sdcard/VPK_Extracted') 
    	except:
    		pass     		     	    		     		
    	
    	try:
    		
    		
    	
    	    from pathlib import Path
    	    import vpk
    	    
    	    import subprocess
    	    ff = Path('/sdcard/VPK_Extracted')
            
    	    re=Path('/sdcard/Boo_VPK')
    	    re.mkdir(parents=True, exist_ok=True)
    	    ff.mkdir(parents=True, exist_ok=True)
    		
    	except:
    		self.label22.color=(1,0,0,1)
    		self.label22.text="Error : Please Grant Files Permissions"
    		self.dialog_dismisss()
    		self.show_dialogg("Error ", "Please Grant Files Permissions")
    		
        		
        		
    		return
    	try:
    	
    	    with vpk.open(valuee) as package:
    	    	for entry_name in package:
    	    		fekk = package[entry_name].read()
    	    		full_path = os.path.join('/sdcard/VPK_Extracted', entry_name)
    	    		os.makedirs(os.path.dirname(full_path), exist_ok=True)
    	    		with open(full_path, 'wb') as output_file:
    	    		 	output_file.write(fekk)
		          	
	
		
		
		
		
    	    		
    	    shutil.make_archive(f'/sdcard/Boo_VPK/{woww}', 'zip', '/sdcard/VPK_Extracted')
    	    
    	    self.dialog_dismisss()
    	    self.show_dialogg("Extracted !", "Saved To /sdcard/Boo_vpk")
        			
    	    shutil.rmtree('/sdcard/VPK_Extracted')
    	except ValueError:
    	    		self.label22.color=(1,0,0,1)
    	    		
    	    		self.dialog_dismisss()
    	    		self.show_dialogg("Error ", "Error : This is Not a VPK file.")
    	    		
    		
    	    		return
    	except FileNotFoundError:
    	    		
    	    		self.dialog_dismisss()
    	    		self.show_dialogg("Error ", "File Doesn't Exist, Check The\nFile Path, and Try Again.")
    	    		
    		
    	    		return
    	    		
    	except Exception as fe:
    		self.label22.text=str(fe)    
    


    
  
    
        
    	
    
    	       
    	
    		
    		
    		
    		
    		
    	
   
        
    	
    		
    	
    		
    		
    		
    	
    		
    		
    		
    		
    
    		
    	
    
    


    


    
    	
    			
    		
    	
    	
    		
    	
    	
    	
    	
    	






    	    
    	        
    	                
    def on_submit(self,instance):
        
        try:
        	
        	shutil.rmtree('/sdcard/lon')
        	shutil.rmtree('/sdcard/extracted')
        	os.remove('/sdcard/thefile.7z')
        except:
        	
        	pass
        try:
        	from pathlib import Path
        	ff=Path('/sdcard/lon')
        	ww=Path('/sdcard/Boo_url')
        	hh=Path('/sdcard/extracted')
        	ko=Path('/sdcard/Boo_extracted')
        	ff.mkdir(parents=True, exist_ok=True)
        	ww.mkdir(parents=True, exist_ok=True)
        	hh.mkdir(parents=True, exist_ok=True)
        	ko.mkdir(parents=True, exist_ok=True)
        except:
        	self.label22.color=(1,0,0,1)
        	self.label22.text="Error : Please Grant Access Files Permission."
        	return
        
        
        
        
        
        
        
        
        
        
        value=self.text_inputt.text
        
        
    
        
        
    	   	
    	   	
    	   	
    	
    	   	
        try:
        	
    	   
    	   	
        	import lzma
        	wow = value.split('/')[-1]
        	
    	   	
        	
        	sss = requests.post('https://ytshorts.savetube.me/api/v1/steam-workshop-downloader', data={'url': self.text_inputt.text})
        	if sss.status_code == 200:
        		woow = sss.json()
        		de = woow['response']
        		if de[0]['file_url']=='':
        			self.label.color=(1,0,0,1)
        			self.label.text="This Mod is Not Available in SWD."
        			return
        		
        		gh = de[0]['file_url']
        		ghh = de[0]['title']
        		jj = requests.get(gh)
        		with open('/sdcard/thefile.7z', 'wb') as f:
        			f.write(jj.content)
        		with lzma.open('/sdcard/thefile.7z') as f:
        			file_content = f.read()
        		with open('/sdcard/lon/qqq.gma', 'wb') as g:
        				g.write(file_content)
        		
        		
        		
        		
        				
        		dirr = '/sdcard/lon/qqq.gma'
        
        		if dirr.endswith('.gma'):
        			with open(dirr, "rb") as file:
        				gma = GMAVerifiedContents.parse_stream(file)
        				for i in range(0, len(gma.content.all_file_meta) - 1):
        					meta = gma.content.all_file_meta[i]
        					gma_file_name = meta.data.file_name
        					file_name = os.path.join('/sdcard/extracted', gma_file_name)
        					
      
        					file_folder = os.path.dirname(file_name)
        					if not os.path.exists(file_folder):
        						
        						os.makedirs(file_folder)
        					with open(file_name, "wb") as output:
        						output.write(gma.content.embedded_files.contents[i])
        		
    
        					
        		shutil.make_archive(f'/sdcard/Boo_url/{ghh}', 'zip', '/sdcard/extracted')
        		endd= '/sdcard/Boo.zip'
        		self.label.pos_hint=({'center_x': 0.57, 'center_y': 0.90})
        	
        		self.dialog_dismisss()
        		self.show_dialogg("Extarcted !", "Saved To /sdcard/Boo_url")
        		
        			
        		os.remove('/sdcard/lon/qqq.gma')
        		os.remove('/sdcard/thefile.7z')
        		
        	
        		
        		
    	   	
    	   	
        		for root, dirs, files in os.walk('/sdcard/extracted', topdown=False):
        			
        			for name in dirs:
        				folder_path = os.path.join(root, name)
        				shutil.rmtree(folder_path)
        			for jj in files:
        				intok = os.path.join(root, jj)
        				os.remove(intok)
        			
        		
            
          	  
        	
        	
        		
        			
        	else:
        			self.label.color=(1,0,0,1)
        			self.label.text="Error, Check your Connection, Or the link is not\nValid"
        			self.dialog_dismisss()
        			self.show_dialogg("Error", "Check your Connection, Or the link is not Valid")
    		
        				
    		
        			return
        		
        		
        			
        		
        	
        except requests.exceptions.ConnectionError:
        				self.label.color=(1,0,0,1)
        				
        				self.dialog_dismisss()
        				self.show_dialogg("Error", "Please Check your Internet Connection")
    		
    		
        				return
        except PermissionError :
        					self.label.color=(1,0,0,1)
        					self.label.pos_hint=({'center_x': 0.57, 'center_y': 0.90})
        					
        					self.dialog_dismisss()
        					self.show_dialogg("Error", "Failed, Grant Access Files Permission.")
        				
        					return
        except FileNotFoundError:
        						
        						self.label.pos_hint=({'center_x': 0.57, 'center_y': 0.90})
        						self.label.color=(0,1,0,1)
        						
        						self.dialog_dismisss()
        						self.show_dialogg("Extracted !", "Extracted Succeeded ! Saved to /sdcard/Boo_url.")
        					
        						
        						for root, dirs, files in os.walk('/sdcard/extracted', topdown=False):
        							for name in dirs:
        								folder_path = os.path.join(root, name)
        								shutil.rmtree(folder_path)
        							for jj in files:
        								intok = os.path.join(root, jj)
        								os.remove(intok)
        						return
        				
        				
        			
        				
        				
        							
        						
        		
        		
        					
        					
        		
        except Exception as Fr:
    					self.label.text=str(Fr)
    					return			
    @mainthread					
    def dialog_dismisss(self):
        self.dialog.dismiss()
        
        
        
        self.label.text=""
        if self.dialog and self.dialog._is_open:
            self.dialog.dismiss()					
    				
    			
       
    def on_button_press(self, path: str):
    
    	
    	try:
    	   	shutil.rmtree('/sdcard/lon')
    	   	shutil.rmtree('/sdcard/extracted')
    	   	os.remove('/sdcard/thefile.7z')
    	except:
    	   	pass
        	
        	
        	
        
        	
        	
    	
    	
    	
    	value=self.text_input.text
    	
    	
    	
    	if self.show_file_manager==True:
    		self.exit_manager()
    	
    	
    	
        	
        
    	try :
    	   	
    	   	
    	   	wow = value.split('/')[-1]
    	   	woww = wow.split('.')[-2]
        	
    	   	with open(value, "rb") as file:
    	   		gma = GMAVerifiedContents.parse_stream(file)
    	   		from pathlib import Path
    	   		folder_path = Path(f'/sdcard/extracted')
    	   		fff=Path(f'/sdcard/Boo_extracted')
    	   		folder_path.mkdir(parents=True, exist_ok=True)
    	   		fff.mkdir(parents=True, exist_ok=True)
    	   		for i in range(0, len(gma.content.all_file_meta) - 1):
    	   			meta = gma.content.all_file_meta[i]
    	   			gma_file_name = meta.data.file_name
    	   			file_name = os.path.join('/sdcard/extracted', gma_file_name)
    	   			file_folder = os.path.dirname(file_name)
    	   			if not os.path.exists(file_folder):
    	   					os.makedirs(file_folder)
    	   			with open(file_name, "wb") as output:
    	   				output.write(gma.content.embedded_files.contents[i])
    	   	dirrr = os.path.join('/sdcard/Boo_extracted')
    	   	if not dirrr:
    	   	     self.label.color=(1,0,0,1)
    	   	     
    	   	     return
    	   	shutil.make_archive(f'/sdcard/Boo_extracted/{woww}', 'zip', '/storage/emulated/0/extracted')
    	   	
    	   	
    	   	
    	   	   	
    	   	   	
    	   	   	
    	   	   	
    	   	   	
    	   	   		
    	   	   	
    	   	   	
    	
   	
    	   	   		
    	   	
    	   	   	
    	   	   	
    	   	   	
    	   	   	
    	   	   	
    	   	
        		
    	   	 
    	   	 
    	   	
    	   	for root, dirs, files in os.walk('/sdcard/extracted', topdown=False):
    	   			for name in dirs:
    	   						folder_path = os.path.join(root, name)
    	   						shutil.rmtree(folder_path)
    	   			for jj in files:
    	   				intok = os.path.join(root, jj)
    	   				os.remove(intok)
    	   	self.label.pos_hint=({'center_x': 0.60, 'center_y': 0.90})	
    	   	self.label.color=(0,1,0,1)
    	   	
    	   	self.dialog_dismisss()
    	   	self.show_dialogg("Extracted !", "Saved to /sdcard/Boo_extracted.")
    
    	   
    
    	   
    
    	   	
    	   	
    	   		
    	   		
    	   		
    	except ConstError:
    		self.label.color = (1,0,0,1)
    		self.label.pos_hint=({'center_x': 0.60, 'center_y': 0.90})
    		
    		self.dialog_dismisss()
    		
    		self.show_dialogg("Error", "This is not a Gmad File, Read Errors.")
    		
    		return		
    	except IndexError:
    	   	   	self.label.color = (1,0,0,1)
    	   	   	self.label.pos_hint=({'center_x': 0.60, 'center_y': 0.90})
    	   	   	self.dialog_dismisss()
    	   	   	self.show_dialogg("Error", "make sure to put the right path to your .gma file")
    		
    		
    	   	   	
    	   	   	
    	   	   	return
    	except FileNotFoundError:
    	   	   	self.label.color = (1,0,0,1)
    	   	   	self.label.pos_hint=({'center_x': 0.60, 'center_y': 0.90})
    	   	   	self.dialog_dismisss()
    	   	   	self.show_dialogg("Error", "Please Grant Files Permission., or the file does not exist")
    		
    	   	   
   
    	   	   	return
    	   	   	
    	
    	   	
    	   		   
    	   		
    	   	

    	            
    	except Exception as fe:
    	   	   	self.label.color = (1,0,0,1)
    	   	   	self.label.pos_hint=({'center_x': 0.58, 'center_y': 0.90})
    	   	   	self.dialog_dismisss()
    	   	   	self.show_dialogg("Error", f"Error : {fe}")
    	   	   	self.label.text=str(fe)
    	   	   	return
    	    
        
        
        
        
        
        
        
        
        
        

    def switch_to_second_layout(self, instance):
        self.screen_manager.current = "second"

    def switch_to_main_layout(self, instance):
        self.screen_manager.current = "main"
    def switch_to_third(self, instance):
    	self.screen_manager.current = "third"

MainApp().run()