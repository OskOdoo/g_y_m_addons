openerp.oepetstore = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var website = openerp.website;

    local.HomePage = instance.Widget.extend({
 
        start: function() {
          var text = "", mobile_typed="";
        document.addEventListener("keypress", function(e) {
       var input = document.getElementById('inputURL');
       text = text+e.key;
       mobile_typed = text;
       if (e.target.tagName !== "INPUT" && input && e.keyCode !== 13) {
 
       
         input.focus();
         input.value = e.key;
       e.preventDefault();
       }

       if(e.keyCode === 13){text="";}
      });
          /*************************MOVILE********************************/

        /*****************************HAHAHAHAHA****************************/

            this.$el.append(QWeb.render("HomePageTemplate"));

            var inp = document.getElementById('inputURL');
            inp.focus();
            document.addEventListener("keydown", function(e) {
              //alert("e.keydown = "+e.data+" text.keycode = "+e.keycode +" decode = "+String.fromCharCode(e));
              ////////////////////////treatme///////////////////////
              if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
              
              if (e.target.tagName !== "INPUT" && e.keyCode !== 13){
                //alert("hwa malek= " +text);
              text = text+e.key;
              

              }
             inp.focus();
            

       }
        if (e.keyCode === 13) {
        var url ="",code = text;
        
        if (!code){
          code=inp.value;
        }
        /*************************************/
        var date =""+(new Date()).getFullYear();
        var id="" ;
        model = 'gym.adherent';
        if(code){
          
          var self = this;
        model = 'gym.adherent';

        var mod2 = new instance.web.Model(model)
            .query(['default_code', 'id'])
            .filter([['default_code', '=', code]]).limit(1)
            .all().then(function(ir_model_datas) {
         for (i in ir_model_datas) {
         id=ir_model_datas[i].id;
         var action = {
              type: 'ir.actions.act_window',
              res_model: 'gym.adherent',
              view_type:'form',
              view_mode: 'form',
              res_id: id,
              views: [[false, 'form']],
              
        }
        instance.client.action_manager.do_action(action);
        if(e.keyCode === 13){text="";
        if (id){
        inp.value="";}}
        inp.focus();

      }
    });

                  }//end if adherent
                     

            if((code.includes("E") &&  !id)){
        //  var action4 = "379",
        //  model3 = "sale.order",
          //view_type2="form",id1="";
          //var sale = new Model('sale.order');
          //sale.call('name_search', ['',[]], { context: website.get_context()});
       //url = "web#id="+id1+"&view_type="+view_type2+"&model="+model3+"&action="+action4;
              var today = new Date();
              var dd = today.getDate();
              var mm = today.getMonth()+1; //January is 0!
              var yyyy = today.getFullYear();
              function addZero(i) {
                      if (i < 10) {
                        i = "0" + i;
                      }
                      return i;
                    }
              var h = addZero(today.getHours());
              var m = addZero(today.getMinutes());
              var hour = h + "." + m;

      if(dd<10) {
          dd = '0'+dd
      } 

      if(mm<10) {
          mm = '0'+mm
      } 

      today = yyyy + '-' + mm + '-' + dd; 


          
          var self = this;
        model = 'hr.employee';
        var mod = new instance.web.Model(model)
            .query(['otherid', 'id'])
            .filter([['otherid', '=', code]]).limit(1)
            .all().then(function(ir_model_datas) {
         for (i in ir_model_datas) {
         id=ir_model_datas[i].id;
         name=ir_model_datas[i].name;
         var action = {
              type: 'ir.actions.act_window',
              res_model: model,
              view_type:'form',
              view_mode: 'form',
              res_id: id,
              views: [[false, 'form']],
              
        };

      model = 'jour.heure';

      var fields = new instance.web.Model(model)
      .call('return_values', [id])
      .then(function(ir_model_datas){

      var values = Object.keys(ir_model_datas).map(function(key){
         console.log('Values dict : '+' '+ir_model_datas[key])
      });

        for (var i in ir_model_datas) {
          console.log('i = '+' '+[i])
      }
      });
/*
      var mod = new instance.web.Model(model)
      .call('create', [{'employee_id': id,'date':today,'action':action,'heure_debut':hour}])
       .then(function(id){
         console.log('fields :'+' '+fields)
      });     
*/

/* 
     action = ''
     model = 'jour.heure';
     var mod = new instance.web.Model(model)
     .query(['employee_id','date', 'heure_debut'])
            .filter([['date', '=', today],['employee_id','=',id]])
            .all().then(function(ir_model_datas) {
         for (i in ir_model_datas) {
                i.call('create', [{'employee_id': id,'date':today,'action':action,'heure_debut':hour}])
                .then(function(id){
                   console.log('Bienvenue'+ '' +i)
                   alert('heeùmmm'+i)
                });

         i.call('write', [{'heure_fin':hour}])
                .then(function(id){
                   console.log('Bienvenue'+ '' +id)
                });

                }
});

*/



        instance.client.action_manager.do_action(action);
        if(e.keyCode === 13){text="";
        inp.value="";}
        inp.focus();
        e.preventDefault();


           }
          });


                  }//end pointage  



        }});




        } //end function start
        ,
        changee: function(e) {
          alert("rani tchangiit");
        }//end of rechercher
        ,
 
    });

    instance.web.client_actions.add('petstore.homepage', 'instance.oepetstore.HomePage');

 

}
