1.系統代表名稱（英文）:
oia_ncku_osss
2.系統中文名稱 :
國際處機器人單一登入
3.系統伺服器回傳網址：
login.nckuoiachatbot.software
4.client-id: 16ea6d31-ca5d-4f39-99f3-bcdd801121fb


下面是設定範例：

$base_url = "https://i.ncku.edu.tw";
$server_url = "https://fs.ncku.edu.tw";
$oauth2_clients['oia_ncku_osss'] = array(
    'token_endpoint' => $server_url . '/adfs/oauth2/token',
    'auth_flow' => 'server-side',
    'client_id' => '16ea6d31-ca5d-4f39-99f3-bcdd801121fb',
    'client_secret' => 'oia_ncku_osss',
    'authorization_endpoint' => $server_url . '/adfs/oauth2/authorize',
    'redirect_uri' => 'https://login.nckuoiachatbot.software',
);