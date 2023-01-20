var WinHttpReq = new ActiveXObject("WinHttp.WinHttpRequest.5.1");
WinHttpReq.Open("GET", "https://www.python.org/ftp/python/3.8.6/python-3.8.6-embed-win32.zip", /*async=*/false);
WinHttpReq.Send();
/* WScript.Echo(WinHttpReq.ResponseText); */

BinStream = new ActiveXObject("ADODB.Stream");
BinStream.Type = 1;
BinStream.Open();
BinStream.Write(WinHttpReq.ResponseBody);
BinStream.SaveToFile("python-3.8.6-embed-win32.zip");
