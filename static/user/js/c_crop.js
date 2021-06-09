var $image = $('#image');

$image.cropper({
  aspectRatio: 16 / 9,
  crop: function(event) {
    console.log(event.detail.x);
    console.log(event.detail.y);
    console.log(event.detail.width);
    console.log(event.detail.height);
    console.log(event.detail.rotate);
    console.log(event.detail.scaleX);
    console.log(event.detail.scaleY);
  }
});

//Instantiate
var cropper = $image.data('cropper');


var $image = $('#target');
$('[type=file]').change(function(e) {
    var file = e.target.files[0]
    if(file.size>= 2*1024*1024){
        layer.alert('The avatar you uploaded is larger than 2M, please upload again', {
            title:'prompt',
            icon: 0,
            skin:'layui-layer-lan', //This skin is kindly extended by layer.seaning.com. For the expansion rules of the skin, go here to check
        });
    }else{
        var reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload=function(e){
            $image.attr("src",e.target.result)
            $image.cropper('reset', true).cropper('replace',e.target.result);
        }
        if(($('#target').attr('src').length) != 0){
            $('#preview').show()
            $('#preview-pane').show()
            $('.crop-operate').show()
        }
    }
})
$image.cropper({
    dragMode: 'move',
    viewMode:3,
    aspectRatio:1,//1 / 1, //Picture ratio, 1:1
    minCropBoxWidth:300,
    minCropBoxHeight:300,
    minContainerWidth:300,
    minContainerHeight:300,
    restore: false,
    guides: false,
    center: false,
    highlight: false,
    cropBoxMovable: false,
    cropBoxResizable: false,
    toggleDragModeOnDblclick: false,
    modal:false,
    responsive:false,
    preview:'.preview-container',
    background:false,
});

$('#thumb_upload').submit(function(){
    event.preventDefault();
    // Get the base64 of the picture after cropping
    var $imgData=$image.cropper('getCroppedCanvas')
    var dataurl = $imgData.toDataURL('image/jpeg');
    // Convert base64 to blob format
    var b64 = dataurl.split(',')[1];
    var binary = atob(b64);
    var array = [];
    for (var i = 0; i < binary.length; i++) {
        array.push(binary.charCodeAt(i));
    }
    var blob =  new Blob([new Uint8Array(array)], {type: 'image/jpeg'})
    // Use FormData() to make ajax requests and upload pictures
    var formData = new FormData()
    // Picture name
    var img_name = new Date().getTime()+'.jpg';
    formData.append('csrfmiddlewaretoken','{{ csrf_token }}')
    formData.append('uploadFile',blob,img_name)
    var data = formData
    $.ajax({
        url: "/Upload address/",
        type: "post",
        dataType: "json",
        data:data,
        processData: false,
        contentType:false,
        success:function(result){
            if(result['state']==0){
               layer.close(layer.index);
               window.parent.location.reload();
            }
            if(result['state']==1){
                layer.alert('Upload failed, please contact customer service', {
                    title:'prompt',
                    icon: 0,
                    skin: 'layui-layer-lan'//This skin is kindly extended by layer.seaning.com. For the expansion rules of the skin, go here to check
                },
                function (){
                    window.parent.location.reload()
                }
                );
            }
        }
    });
});

$('#cancel').click(function(){
    event.preventDefault();
    var index = parent.layer.getFrameIndex(window.name);
    parent.layer.close(index);
})
