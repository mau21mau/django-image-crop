debug = "";
var overlay;
var crop_api;
var crop_api;
var xhr;
function ajax_file_upload(input, model_package, model_name, attr_name){
    
    var file = input.files[0];
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var formData = new FormData;
    
    formData.append(attr_name, file);
    formData.append('csrfmiddlewaretoken', csrfmiddlewaretoken);
    
    formData.append('model_name', model_name);
    formData.append('package', model_package);
    formData.append('attr_name', attr_name);
    
    if (window.instance_id > 0){
        formData.append('id', window.instance_id);
    }

    xhr = new XMLHttpRequest();
    //xhr.file = file; // not necessary if you create scopes like this
    
    xhr.addEventListener('progress', function(e) {
        var done = e.position || e.loaded, total = e.totalSize || e.total;
        console.log('xhr progress: ' + (Math.floor(done/total*1000)/10) + '%');
    }, false);
    
    xhr.addEventListener("load", function(){
        console.log("Upload completo!");
        
        overlay.hide(null, "O envio foi concluído!", 3000, "concluido", null);
        
    }, false);
    
    xhr.addEventListener("error", function(){
        
        overlay.hide(null, "Falha ao enviar! Tente novamente.", 3000, "erro", null);
        
    }, false);
    
    if ( xhr.upload ) {
        xhr.upload.onprogress = function(e) {
            var done = e.position || e.loaded, total = e.totalSize || e.total;
            //console.log('xhr.upload progress: ' + done + ' / ' + total + ' = ' + (Math.floor(done/total*1000)/10) + '%');
            $("#loading-bar").val((Math.floor(done/total*1000)/10)).trigger('change');
            console.log( (Math.floor(done/total*1000)/10) + '%' );
        };
    }
    
    xhr.onreadystatechange = function(e) {
        if ( 4 == this.readyState ) {
            console.log(['xhr upload complete', e]);
            debug = xhr.responseText;
            var json_object = jQuery.parseJSON(xhr.responseText);
            window.instance_id = update_form(json_object, attr_name);
            
            var app_label = model_package.split(".")[0];
            console.log("ID da instancia: "+instance_id);
            window.history.pushState("object or string", "Title", "/admin/"+app_label+"/"+model_name.toLowerCase()+"/"+window.instance_id+"/");
            location.reload();
        }
    };
    
    xhr.open('POST', "/imagecrop/upload/", true);
    overlay.show("Uploading...", "uploading", "loading-image");
    xhr.send(formData);
}

function url_file_upload(url_image){
    var csrfmiddlewaretoken = $("input[name=csrfmiddlewaretoken]").val();
    var url = $("#url_upload_external").val();
    var post_data = {"csrfmiddlewaretoken":csrfmiddlewaretoken, "url": url_image };
    
    var modulo = $("#nome_modulo").val();
    
    if (modulo == "review"){
        var autor = $("#id_autor").val();
        if (autor == ""){
            alert("Você deve selecionar um autor!");
            return false;
        }else{
            post_data['autor'] = autor;
        }
    }
    
    $.ajax({
        type : "POST",
        data: post_data,
        url : url,
        beforeSend : function() {
            overlay.show("Uploading...", "uploading", "loading-url");
        },
        complete : function() {
            
        },
        success : function(result) {
            debug = result;
            var json_object = eval(result);
            var instance_id = update_form(json_object);
            
            var url = "/"+modulo_plural+"/imagem/crop/"+instance_id+"/";
            var url_external = "/"+modulo_plural+"/imagem/crop/url/"+instance_id+"/";
            $("#url_upload").attr('value', url);
            $("#url_upload_external").attr('value', url_external);
            
            console.log("ID da instancia: "+instance_id);
            window.history.pushState("object or string", "Title", "/admin/core/"+modulo_singular+"/"+instance_id+"/");
            overlay.hide(null, "Envio concluído!", 5000, "concluido", null);
        },
        error : function(error) {
            // msg_confirm, msg status, tempo fadout, status mensagem
            overlay.hide(null, error+"Erro ao enviar!", 5000, "erro", null);
        }
    });
}

function build_crop(img){
    var images = $(".crop");

    $(".previous").removeClass("previous");
    if ( !$(img).hasClass("current") && images.length > 0 ){
        $(".current").addClass("previous");
        $(".previous").removeClass("current");
        destroy_crop($(".previous"));
    }

    $(img).addClass("current");

    var original_src = $(img).attr("data-originalsrc");

    $(img).attr('src', original_src).load(function() {
        var original_dim = $(img).attr("data-originalsize");
        var original_with = parseInt(original_dim.split(",")[0]);
        var original_height = parseInt(original_dim.split(",")[1]);
        $(img).css("width",original_with+"px");
        $(img).css("height",original_height+"px");

        var cropped_dim = $(img).attr("data-size");
        var cropped_width = parseInt(cropped_dim.split(",")[0]);
        var cropped_height = parseInt(cropped_dim.split(",")[1]);

        var box = getBox(original_with, original_height, cropped_width, cropped_height);
        crop_api = $(img).imgAreaSelect({
            x1: box[0],
            y1: box[1],
            x2: box[2],
            y2: box[3],
            instance: true,
            imageHeight: original_height,
            imageWidth: original_with
        });

    });

    //console.log(attr_name);
    var this_url = $(img).attr("rel");


    // Apos a imagem anterior ser restabelecida, este blobo ira iniciar
    // a nova instancia do JCROP para imagem atual

    var cropable_dim = $(img).attr("data-originalsize").split(",");

    $("#image-loading-overlay").hide();
}

function crop_img(c, attr_name, id){
    //console.log(attr_name);
    corte_left = Math.round(c.x);
    corte_up = Math.round(c.y);
    corte_right = Math.round(c.x2);
    corte_down = Math.round(c.y2);
    
    $.ajax({
        type : "GET",
        url : '/'+modulo_plural+'/imagem/crop/'+id+'/'+corte_left+'/'+corte_up+'/'+corte_right+'/'+corte_down+"/"+attr_name+"/",
        beforeSend : function() {
            show_image_loading( $(".crop-holder") );
        },
        complete : function() {
            
        },
        success : function(result) {
            
            try{
               crop_api.destroy();
               // ESTE BLOCO REDIMENSIONA A IMAGEM PARA SEU TAMANHO ORIGINAL
               // PARA QUE NÃO FIQUE ESTICADA
               var original_dim = $(".current").attr("data-size");
               var original_height = parseInt(original_dim.split(",")[1].replace(")",""));
               var original_width = parseInt(original_dim.split(",")[0].replace("(",""));
               $(".current").css("height", original_height+"px");
               $(".current").css("width", original_width+"px");
            }catch(err){
                a=1;
            }
            
            var instance_json = eval("("+result+")");
            debug = instance_json;
            var atributo = instance_json.atributo;
            $("#"+atributo).fadeOut(500, function(){
                $("#"+atributo).css("visibility", "visible");
                $("#"+atributo).attr("src", "/media/"+instance_json[atributo]).stop(true,true).hide().fadeIn();
            });
                    
            // Seta o atributo data-originalsrc apontando para imagem cropada afin de restaurar-la
            // quando for clicado em outra imagem para faer crop
            $("#"+atributo).attr("data-originalsrc", "/media/"+instance_json[atributo]);
            $("#id_"+atributo).val(instance_json[atributo]);
            $("#image-loading-overlay").hide();
        },
        error : function(error) {
            var div_error = "<div id='getsrc-status'>Erro de conexão! Tente novamente</div>";
            $("#image-loading").fadeOut("slow", function(){
                $("#image-loading-overlay").html(div_error);
                $("#getsrc-status").css("margin", ( $(".crop-holder").height() / 2 - $("#getsrc-status").height() )+"px auto" );
                $("#getsrc-status").fadeIn('slow', function(){
                    window.setTimeout(function(){
                        $("#image-loading-overlay").hide();
                    }, 4000);
                });
            });
        }
    });

}

function getBox(original_width, original_height, cropped_largura, cropped_altura) {
    original_width = parseInt(original_width);
    original_height = parseInt(original_height);
    cropped_largura = parseInt(cropped_largura);
    cropped_altura = parseInt(cropped_altura);

    corte_left = ( original_width / 2 ) - ( cropped_largura / 2 );
    corte_up = ( original_height / 2 ) - ( cropped_altura / 2 );
    corte_right = corte_left + cropped_largura;
    corte_down = corte_up + cropped_altura;
    zoera = [Math.round(corte_left), Math.round(corte_up), Math.round(corte_right), Math.round(corte_down)];
    return [Math.round(corte_left), Math.round(corte_up), Math.round(corte_right), Math.round(corte_down)];
}

function update_form(json_object, attr_name){
    var fields = json_object[0].fields;
    var instance_id = json_object[0].pk;
    
    var cropped_src = json_object[0][attr_name+'_cropped']['src'];
    var original_src = json_object[0][attr_name+'_original']['src'];
    var original_dim = json_object[0][attr_name+'_original']['dimensions'];
    var cropped_dim = json_object[0][attr_name+'_cropped']['dimensions'];
    
    for (field in fields){
        try{
            $("#id_"+field).val(fields[field]);
        }catch(Error){
            continue;
        }
    }
    
    $("#imagecrop_"+attr_name).attr("data-originalsize", original_dim);
    $("#imagecrop_"+attr_name).attr("data-size", cropped_dim);
    $("#imagecrop_"+attr_name).attr("data-originalsrc", original_src);
    $("#imagecrop_"+attr_name).attr("data-croppedsrc", cropped_src);
    
    $("#imagecrop_"+attr_name).hide();
    $("#imagecrop_"+attr_name).attr("src", cropped_src);
    $("#imagecrop_"+attr_name).load(function(){
        $("#imagecrop_"+attr_name).fadeIn("slow");
    });
    
    return instance_id;
}

function get_box_field(id){
    var splited_id = id.split("_");
    var last_word = splited_id[splited_id.length-1];
    
    if (last_word == "temp"){
        var hidden_input = id.substr(0, id.lastIndexOf("_"));
    }else{
        var hidden_input = id;
    }
    hidden_input = "id_"+hidden_input+"_cropbox";
    return hidden_input;
}

function show_image_loading(img){
    $("#image-loading-overlay").height($(img).height());
    $("#image-loading-overlay").width($(img).width());
    
    $("#image-loading-overlay").css("top", $(img).position().top+"px");
    $("#image-loading-overlay").css("left", $(img).position().left+"px");
    var image_loading = "<div id='image-loading'></div>";
    $("#image-loading-overlay").html(image_loading);
    $("#image-loading").css("margin", ( $(img).height() / 2 - $("#image-loading").height() )+"px auto" );
    $("#image-loading").show();
    
    $("#image-loading-overlay").show();
}

function destroy_crop(img){
    try{
        crop_api.remove();
        crop_api = null;

        var cropped_dim = $(img).attr("data-size");
        var cropped_height = parseInt(cropped_dim.split(",")[1]);
        var cropped_width = parseInt(cropped_dim.split(",")[0]);

        var cropped_src = $(img).attr("data-croppedsrc");

        $(img).attr("src", cropped_src).load(function(){
            $(img).css("width", cropped_width+"px");
            $(img).css("height", cropped_height+"px");
        });

    }catch(err){
        a=1;
        console.log("Erro");
    }
}

$(window).load(function(){
    modulo_plural = $("#nome_modulo").val();
    modulo_singular = $("#nome_modulo").attr("data-singular");
    overlay.init();
    $(window).resize(function () {
        overlay.setDimension();
    });
    
    $("#loading-bar").knob({
        'min': 0,
        'max':100,
        'width':120,
        'height':120,
        'thickness': 0.2,
        'readOnly': true,
        'fgColor':"#9FBFD4",
        'bgColor':"#302A28"
    });
    
    $(".close-loading").click(function(){
        var are_you_sure = confirm("Deseja cancelar o envio ?");
        if ( are_you_sure ){
            if (xhr){
                if (xhr.readyState == 1){
                    xhr.abort();
                }
            }
            
            overlay.hide(null, "Cancelado!", 3000, "cancelado", null);
            
        }
    });
    
    $(document).on("click", "#cancel-crop", function(){
        destroy_crop($(".current"));
    });

    $(document).on("click", ".crop", function(){
        $(this).addClass("current");
        build_crop($(".current"));
    });
    
    
});

overlay = {
    current : "",
    init : function(){
        // CREATE THE OVERLAY
        var attrs = {
            "id":"overlay"
        }
        var body = document.getElementsByTagName("body")[0];
        var overlay_obj = create_dom_object("div",attrs, body);
        overlay_obj.style.display = "none";
        //====================================================================//
        
        // CREATE THE LOADING IMAGE MODAL
        var attrs = {
            "id":"loading-image",
            "class":"imgload-modal",
        }
        var loading_image_obj = create_dom_object("div",attrs, overlay_obj);
        //====================================================================//
        
        // CREATE THE CLOSE BUTTON FOR IMAGE MODAL
        var attrs = {
            "class":"close-loading"
        }
        var span_obj = create_dom_object("span",attrs, loading_image_obj);
        var text = document.createTextNode("X");
        span_obj.appendChild(text);
        //====================================================================//
        
        // CREATE INPUT FOR KNOB-LOADING PLUGIN
        var attrs = {
            "type":"text",
            "id":"loading-bar"
        }
        var input_obj = create_dom_object("input",attrs, loading_image_obj);
        //====================================================================//
        
        // CREATE THE P OBJECT
        var attrs = {
            "class":"status-upload"
        }
        var p_obj = create_dom_object("p",attrs, loading_image_obj);
        //====================================================================//
        
        // CREATE THE LOADING URL MODAL
        var attrs = {
            "id":"loading-url",
            "class":"imgload-modal",
        }
        var loading_url_obj = create_dom_object("div",attrs, overlay_obj);
        loading_url_obj.appendChild(span_obj.cloneNode(true));
        loading_url_obj.appendChild(p_obj.cloneNode(true));
        //====================================================================//
    },
    
    setDimension : function(){
        var window_h = window.innerHeight;
        var window_w = window.innerWidth;
        $("#overlay").height(window_h);
        $("#overlay").width(window_w);
        $("#overlay .current").css("top", ( (window_h / 2 - $("#overlay .current").height() / 2) -50 )+"px" );
        $("#overlay .current").css("left",( (window_w / 2) - ($("#overlay .current").width() / 2)-50 )+"px" );
    },
    
    // Certifique-se de setar o atributo 'current' do overlay antes de usar o show
    // O current representa qual o loding será exibido (eh o id da div container do loading)
    show : function(msg_status, status, modal){
        $(".current").removeClass("current");
        $("#"+modal).addClass("current");
        
        this.setDimension();
        
        var previous_class = $("#"+modal+" p").attr("class");
        if (previous_class){
           $("#"+modal+" p").removeClass(previous_class).addClass(status);
        }else{
            $("#"+modal+" p").addClass(status);
        }
        
        $("#"+modal+" p").html(msg_status);
        
        $("#overlay").fadeIn('slow');
        $("#"+modal).fadeIn('slow');
    },
    
    hide : function(msg_confirm, msg_status, tempo, status, callback){
        $("#overlay .current p").html("");
        $("#overlay .current p").html(msg_status);
        
        var previous_class = $("#overlay .current p").attr("class");
        if (previous_class){
           $("#overlay .current p").removeClass(previous_class).addClass(status);
        }else{
            $("#overlay .current p").addClass(status);
        }
        
        if (msg_confirm){
            var are_you_sure = confirm(msg_confirm);
            if ( are_you_sure ){
                window.setTimeout(function(){
                    $("#overlay").fadeOut('slow');
                    $("#overlay").children("div").css("display", "none");
                    
                    if (callback){
                        callback();
                    }
                }, tempo);
            }
        }else{
            window.setTimeout(function(){
                $("#overlay").fadeOut('slow', function(){
                    $("#overlay").children("div").css("display", "none");
                });
                
                if (callback){
                    callback();
                }
            }, tempo);
        }
        
    }
};

function create_dom_object(tagName, attrs, parent){
    var obj = document.createElement(tagName);
    
    for (var attr in attrs){
        var attr_obj = document.createAttribute(attr);
        attr_obj.value = attrs[attr];
        obj.setAttributeNode(attr_obj);
    }
    
    parent.appendChild(obj);
    
    return obj;
    
}
