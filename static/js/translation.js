const languagedict = {
	"t001":["Introduction","介绍"],
	"t002":["Run","运行"],
	"t003":["Principle","原理"],
	"t004":["Manual","手册"],
	"t005":["Reference","引用"],
	"t006":["A tool for calculating Ar-Ar data", "一个服务于Ar-Ar数据处理的网站"]
	}

function changelang2en(){
	for (let entries of Object.entries(languagedict)){
		document.getElementById(entries[0]).innerHTML=entries[1][0];
	}
}
function changelang2cn(){
	for (let entries of Object.entries(languagedict)){
		document.getElementById(entries[0]).innerHTML=entries[1][1];
	}
}
