var WinHttpReq = new ActiveXObject("WinHttp.WinHttpRequest.5.1");
WinHttpReq.Open("GET", "https://bootstrap.pypa.io/get-pip.py", /*async=*/false);
WinHttpReq.Send();
/* WScript.Echo(WinHttpReq.ResponseText); */

BinStream = new ActiveXObject("ADODB.Stream");
BinStream.Type = 1;
BinStream.Open();
BinStream.Write(WinHttpReq.ResponseBody);
BinStream.SaveToFile("get-pip.py");
