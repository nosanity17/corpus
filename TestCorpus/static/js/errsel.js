/*
 * -----------
 * EANC 1.0
 * ��������: gramsel.php
 * �����:    Alexey V.Zelenin (grinka@gmail.com)
 * -----------
 */
/*
-----------
��������:
	
	������������ ��������, �� ������� ���������� ��������: gramsel.php

�������������:

	���� ���������� � ���������. ��� ���������� ������ ��������� "jQuery.js"

�������:
	function parse_grms(str)
	function collect()
	function inverse(group)
	function InitWindow()

��. �����:
	gramsel.php
-----------
*/

/*
-----------------------------------------------------------------------------------------
function parse_grms(str)

��������:
	���������� ������ ������, ���������� �������� � ������. ������ ���������� �����
	javascript �� ������������� ����. ������������ ������ ������� � ������������ 
	����������� ��������.

���������:
	str - ������, ������� ���������� ���������

������������:
	������. ���� ������ �����, ������������ ������ ������.
-----------------------------------------------------------------------------------------
*/
function parse_grms(str)
{
	var grms_arr = [];
	if (str == "") return grms_arr;
	var grms_str = new String(str);
	var pattern = /\s*,\s*/
	var groups_list = grms_str.split(pattern);
	var re = /\(([\w ]+)\)/
	var ind = 0;

	for (i = 0; i < groups_list.length; i++)
	{
		if (re.test(groups_list[i])) {
			grms_str = groups_list[i].replace(re, "$1");
			var re2 = /\s+/
			grms_list = grms_str.split(re2);
			for (j = 0; j < grms_list.length; j++)
			{
				grms_arr[ind++] = grms_list[j];
			}
		} else {
			grms_arr[ind++] = groups_list[i];
		}
	}
	return grms_arr;
}
/*
-----------------------------------------------------------------------------------------
function collect()

��������:

	���������� ���� ���������� � ����� (���������� ��������)
	� ������� ��� ���������� � ������������ ����.
	����� �������� ������, ������������ �������� ���������� ��������� �����
	"|", ��������� � � ������������ ���� ��� ������������� ��� ��������� ��������
	����� "gramsel.php". ��� ������ ����� ����� �������������� � ������� InitWindow

	���������� ������� �������������� ���������� ���� "flex" - ��� ��������� 
	������������ ���������� ���� �����.
	
�������������:

	������� ���������� ��� ����� �� ������ �����.

-----------------------------------------------------------------------------------------
*/
function collect()
{
  // ��� �������� �����
  var els = '';
  els = document.getElementById('gramForm').elements;

  // ������ ��� ��������
  var ar = '';
  ar = {};

	// ������, ������� ����� ������������ ������������� ���� ��� ����������
  var valuesList = '';

  for (var i = 0; i != els.length; i++)
	{
        var el = els[i];
		// ������������ ������ ��������
        if (el.type != 'checkbox') continue;

        if (el.checked)
		{
			// ���� ������� ������
			// ��������� ��� �������� � ������ ��� ����������
			valuesList += '|' + el.value;
			// �������������� �������� � �������, ���� ������ ��� �� ����
			// ���� - ��� ��������
		            if (!ar[el.name]) 
				ar[el.name] = '';
			// ��������� �������� �������� � �������� �������
			// magical hack
			ar[el.name] += '|' + el.value;
    }
  }

	// �������� � ������ ��� �������� ���������.
	// �������� � ����������� ������� ������������ ����� "|"
	// ������ ��������� ��������������� ����� ","
	// ���� � ������ ������ ������ ��������, ��� ������������ � ������� ������� ������
	var s;
	s = '';
	for (i in ar)
	{
		// �������� ������ ������, ��� ��� ��� ����� ������ ������������� ������������
		// ����� "|" � ������ ������ ������ ����� "|"
		var v = '';
		v = ar[i].substring(1)
		// ��������� ��������, ���� ���������
		if (v.indexOf('|') != -1)
			v = '(' + v + ')';
		// ��������� ����� �������
		s += ',' + v;

	}

	// �������� ������ �������
  s = s.substring(1);

  sourceName = window.name;
  if (window.opener && !window.opener.closed)
	{
		// ������� ��������� ������������� ����
		// ������ ��������� � �����������. ����� ���-�� �������������� ������������ �����
        window.opener.document.forms[0].elements[sourceName].value = s;
		// ������ �������� ��������� ��� ����������. ����� �������������� ��� ���������
		// �������� ���� ������ ���������
		if(window.opener.acceptGramcodesList)
			window.opener.acceptGramcodesList(sourceName, valuesList);
		// ������ ������� ���������, � ������� ������������ ������ ��������� ���������
		// window.opener.document.getElementById("span_" + sourceName).style.display = "";
	}
  window.close();
}

function collectLexiconFormValues()
{
	var 
		valuesList = {
			toString: "",
			valuesList: ""
		}, 
		foundOne = false,
		hasIntrg = false,
		els = document.getElementById("lexForm").elements;
	for(var i = 0, len = els.length; i < len; i++)
	{
		var el = els[i];
		if(el.type != 'checkbox')
			continue;
		if(el.checked)
		{
			if(el.value == "intrg")
			{
				hasIntrg = true;
				continue;
			}
			var cmplValue = "";
			cmplValue =
				(el.value.indexOf(",") > -1) ?
				"(" + el.value + ")" :
				el.value;
			valuesList.toString += 
				(foundOne ? "|" : "") +
				cmplValue;
			valuesList.valuesList += (foundOne ? "|" : "") + el.value;
			foundOne = true;
		}
	}
	if(hasIntrg)
	{
		if(valuesList.valuesList.length == 0)
		{
			valuesList.valuesList = "intrg";
			valuesList.toString = "intrg";
		}
		else
		{
			valuesList.valuesList += "|" + "intrg";
			valuesList.toString = "(" + valuesList.toString + "),intrg";
		}
	}
	return valuesList;
}

/*
-----------------------------------------------------------------------------------------
function inverse(group)

��������:

	����������� ���������� ������ ��������� � ����� ���������.

�������������:

	���������� ��� ����� �� ��������� ����� �� �����.

-----------------------------------------------------------------------------------------
*/
function inverse(group)
{
    var els = document.gramForm.elements;
    var ar = {};
    for (var i = 0; i != els.length; i++) {
        var el = els[i];
        if (el.type != 'checkbox') continue;
        if (el.name == group)
            el.checked=!el.checked;
    }
}

/*
-----------------------------------------------------------------------------------------
function InitWindow()

��������:
	������� ���������� ��� ������������� ��������, �� ������� window.load.
	������������� ��������� �������� ��� ���������, ��������� ������� ���� �
	����� � ������������ ����. � ���� ���� ��� �������� ��������� �����������
	����� "|"

-----------------------------------------------------------------------------------------
*/
function InitWindow()
{
	if(window.opener)
	{
		// �������� �� ������������� ���� ���������� �� ������������� ���������
		// ��������������� ��������� ���������.
		//var openerForm = window.opener.document.forms[0];
		/*
		grms = parse_grms(openerForm.elements[window.name].value);
		var el;
		for (i = 0; i < grms.length; i++)
		{
			el = window.document.getElementById(grms[i]);
			if (el) el.checked = true;
		}
		*/
		// ��������������� �������� ����������, ������� ���� ��������� � ������������ ����
		//  � ����� � ��������� ���� ����� �� ����� "<window.name>_values", ��� window_name -
		// ��� ������� ����������� ���� ��� ����� ���������.
		if(window.opener.getGramcodesList(window.name))
		{
			var valuesList = window.opener.getGramcodesList(window.name);

			// �������� ������ ���� ���������
			if(valuesList != null)
			{
				// �������� � ������. ����������� - "|"
				var valuesArray; 
				valuesArray = valuesList.split("|");
				var els; 
				els = document.forms["gramForm"].elements;
				
				InitFormControls(els, valuesArray);
				//InitFormControls(document.forms["lexForm"].elements, valuesArray);
			}
		}
	}
	// �������������� ����������� ��� 
	//$("#headerTrigger a.grammar").click(showGrammar);
	//$("#headerTrigger a.lexicon").click(showLexicon);
}

function InitFormControls(els, valuesArray)
{
	for(var i = 0; i < els.length; i++)
	{
		var el; 
		el = els[i];
		// ��� ���������
		if (el.type == 'checkbox')
		{
			for (var k = 0; k < valuesArray.length; k++)
			{
				if(el.value == valuesArray[k])
				{
					// ���� �������� �������� �������� ���� ����� ����������,
					// ������������� �������
					el.checked = true;
				}
			}
		}
		// ��� �������� ���������
		if (el.type == 'select-one')
		{
			// ��������� ��� �������� ������ ���������
			for(var j = 0; j < el.length; j++)
			{
				for (var k = 0; k < valuesArray.length; k++)
				{
					if(el.options[j].value == valuesArray[k])
					{
						// ���� �������� ������� - ������ ������ ����� ���������
						el.options[j].selected = true;
					}
				}
			}
		}

	}
}
function showGrammar()
{
	if($("a.grammar").hasClass("activeA"))
		return;
	$("a.grammar").addClass("activeA");
	//$("a.lexicon").removeClass("activeA");
	//$("#main_lexicon").fadeOut();
	$("#main_gram").fadeIn();
}
function showLexicon()
{
	if($("a.lexicon").hasClass("activeA"))
		return;
	$("a.lexicon").addClass("activeA");
	$("a.grammar").removeClass("activeA");
	$("#main_gram").fadeOut();
	//$("#main_lexicon").fadeIn();
}
