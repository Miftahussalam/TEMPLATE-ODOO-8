<html>
<head>
<style>
 
table{
        font-size:10px;
}
 
#header2 th{
        border-bottom:1px solid #000;
}
 
</style>
</head>
<body>
 
    %for o in get_kursus(data):
    <table width="100%">
        <tr>
            <th style='font-size:12pt'>REPORT KURSUS</th>
        </tr>
        <tr>
            <th style='font-size:10pt' align="left">Nama Kursus : ${o.name}</th>
        </tr>
        <tr>
            <th style='font-size:10pt' align="left">Koordinator : ${o.koordinator_id.name}</th>
        </tr>
        <tr>
            <th style='font-size:10pt' align="left">Keterangan : ${o.keterangan}</th>
        </tr>
    </table>
     
    <table width="100%" cellspacing="0" cellpadding="3px">
        <tr>
            <td colspan="12" style="border-bottom:5px double #000;">&nbsp;</td>
        </tr>
        <tr>
            <th style='font-size:12pt'>Name</th>
            <th style='font-size:12pt'>Tanggal Mulai</th>
            <th style='font-size:12pt'>Durasi</th>
            <th style='font-size:12pt'>Kursi</th>
        </tr>
        <tr id="header2">
            <th style='font-size:12pt'>Peserta</th>
            <th>&nbsp;</th>
            <th>&nbsp;</th>
            <th>&nbsp;</th>
        </tr>
        %for i in o.sesi_ids:
        <tr>
            <td style='font-weight:bold; font-size:10pt' align="center">${i.name}</td>
            <td style='font-weight:bold; font-size:10pt' align="center">${time.strftime('%d %B %Y', time.strptime(i.tanggal_mulai,'%Y-%m-%d'))}</td>
            <td style='font-weight:bold; font-size:10pt' align="center">${i.durasi}</td>
            <td style='font-weight:bold; font-size:10pt' align="center">${i.kursi}</td>
        </tr>
            %for x in i.peserta_ids: 
            <tr>
                <td>${x.peserta_id.name}</td>
            </tr>
            %endfor
        %endfor 
    </table>
    %endfor
    
</body>
</html>