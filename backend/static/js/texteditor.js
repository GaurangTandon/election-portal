//var x = "<p>Hi there!!!!!!!!! editor</p><p><span style="font-family: 'arial black', sans-serif;">sdfb dfb dfg bdghdgh d<br /></span><span style="text-decoration: line-through;">asdgf sg sg sdgf sdgf&nbsp;</span></p>"
tinymce.init({
  selector: 'textarea',
  plugins: 'table | wordcount | lists', 
  menubar: '',
  toolbar: "undo redo | formatselect | fontselect | bold italic underline strikethrough forecolor backcolor | alignleft aligncenter alignright alignjustify | numlist bullist | outdent indent",
  height: 900,
  toolbar_mode: 'floating',
  setup: function (editor) {
  editor.on('init', function () {
        this.setContent('HI there!!!!' + editor.id); //function to get manifesto data from db goes here
  });
    }
});

function post_manifesto() //function to post updated manifesto in db
{
  var content =  tinyMCE.activeEditor.getContent();
  console.log(content);

  return false
  
}
