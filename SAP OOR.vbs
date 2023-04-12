If Not IsObject(application) Then
   Set SapGuiAuto  = GetObject("SAPGUI")
   Set application = SapGuiAuto.GetScriptingEngine
End If
If Not IsObject(connection) Then
   Set connection = application.Children(0)
End If
If Not IsObject(session) Then
   Set session    = connection.Children(0)
End If
If IsObject(WScript) Then
   WScript.ConnectObject session,     "on"
   WScript.ConnectObject application, "on"
End If
session.findById("wnd[0]").maximize
session.findById("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode "F00030"
session.findById("wnd[0]/usr/radRB_OPN").select
session.findById("wnd[0]/usr/ctxtS_WERKS-LOW").text = "3321"
session.findById("wnd[0]/usr/ctxtS_WERKS-HIGH").text = "3322"
session.findById("wnd[0]/usr/radRB_OPN").setFocus
session.findById("wnd[0]/tbar[1]/btn[8]").press
session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[1]").select
session.findById("wnd[1]/tbar[0]/btn[0]").press
session.findById("wnd[1]/usr/ctxtDY_PATH").setFocus
session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
session.findById("wnd[1]").sendVKey 4
session.findById("wnd[2]/usr/ctxtDY_PATH").text = "C:\Users\ajarabani\Downloads\"
session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = "OOR.XLSX"
session.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = 3
session.findById("wnd[2]/tbar[0]/btn[0]").press
session.findById("wnd[2]/tbar[0]/btn[11]").press
session.findById("wnd[1]/tbar[0]/btn[0]").press
session.findById("wnd[1]/tbar[0]/btn[11]").press
session.findById("wnd[1]/usr/ctxtDY_FILENAME").caretPosition = 3
session.findById("wnd[1]").sendVKey 11
