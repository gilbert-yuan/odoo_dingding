/**
 * Created by Luforn on 2016-11-22.
 */

mui.init({ swipeBack:true });

mui.ready(function(){
    document.getElementById('aas_wms_logout').addEventListener('tap', function(){
        var access_url = location.href;
        window.location.replace('/web/session/logout?redirect='+access_url);
    });
});
