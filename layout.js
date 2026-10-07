// layout.js
function getControllerLayoutHTML(customLabels = {}) {
    const defaultLabels = {
        back: 'LS',
        left: 'L',
        down: 'D',
        right: 'R',
        ls: 'M2',
        lb: 'LB',
        up1: 'U',
        up2: 'M1',
        lt: 'LT',
        x: 'X',
        y: 'Y',
        rb: 'RB',
        a: 'A',
        b: 'B',
        rt: 'RT',
        rs: 'RS'
    };

    const l = (key) => customLabels[key] !== undefined ? customLabels[key] : defaultLabels[key];

    return `
<div class="controller-panel relative w-[640px] h-[360px] rounded-[30px] bg-slate-950/80 shadow-2xl overflow-hidden flex items-center justify-center border border-white/10">
    
    <!-- 背景画像 (idを追加) -->
    <img id="controller-bg-img" src="controller-bg.png" alt="Controller Layout" class="absolute inset-0 w-full h-full object-contain opacity-50 pointer-events-none" />

    <!-- LS (左端) -->
    <div id="btn-back" class="cb shape-pill-vert" style="left: 30px; top: 120px; width: 52px; height: 86px;" data-key="back" onclick="handleButtonClick('back', '${l('back')}')">${l('back')}</div>
    
    <!-- 方向キー群 (left, down, right) -->
    <div id="btn-left" class="cb shape-circle" style="left: 96px; top: 120px; width: 50px; height: 50px;" data-key="left" onclick="handleButtonClick('left', '${l('left')}')">${l('left')}</div>
    <div id="btn-down" class="cb shape-circle" style="left: 156px; top: 120px; width: 50px; height: 50px;" data-key="down" onclick="handleButtonClick('down', '${l('down')}')">${l('down')}</div>
    <div id="btn-right" class="cb shape-circle" style="left: 216px; top: 140px; width: 50px; height: 50px;" data-key="right" onclick="handleButtonClick('right', '${l('right')}')">${l('right')}</div>
    
    <!-- M2 -->
    <div id="btn-ls" class="cb shape-circle" style="left: 280px; top: 150px; width: 52px; height: 52px;" data-key="ls" onclick="handleButtonClick('ls', '${l('ls')}')">${l('ls')}</div>

    <!-- 下部クラスタ (LB, U, M1, LT) -->
    <div id="btn-lb" class="cb shape-circle" style="left: 205px; top: 236px; width: 50px; height: 50px;" data-key="lb" onclick="handleButtonClick('lb', '${l('lb')}')">${l('lb')}</div>
    <div id="btn-up1" class="cb shape-pill-slant-left" style="left: 270px; top: 236px; width: 64px; height: 82px;" data-key="up1" onclick="handleButtonClick('up1', '${l('up1')}')">${l('up1')}</div>
    <div id="btn-up2" class="cb shape-pill-slant-right" style="left: 342px; top: 236px; width: 64px; height: 82px;" data-key="up2" onclick="handleButtonClick('up2', '${l('up2')}')">${l('up2')}</div>
    <div id="btn-lt" class="cb shape-circle" style="left: 414px; top: 236px; width: 50px; height: 50px;" data-key="lt" onclick="handleButtonClick('lt', '${l('lt')}')">${l('lt')}</div>

    <!-- 6ボタン攻撃エリア (X, Y, RB, A, B, RT) -->
    <div id="btn-x" class="cb shape-circle" style="left: 356px; top: 125px; width: 46px; height: 46px;" data-key="x" onclick="handleButtonClick('x', '${l('x')}')">${l('x')}</div>
    <div id="btn-y" class="cb shape-circle" style="left: 408px; top: 98px; width: 46px; height: 46px;" data-key="y" onclick="handleButtonClick('y', '${l('y')}')">${l('y')}</div>
    <div id="btn-rb" class="cb shape-circle" style="left: 460px; top: 84px; width: 46px; height: 46px;" data-key="rb" onclick="handleButtonClick('rb', '${l('rb')}')">${l('rb')}</div>

    <div id="btn-a" class="cb shape-circle" style="left: 370px; top: 178px; width: 46px; height: 46px;" data-key="a" onclick="handleButtonClick('a', '${l('a')}')">${l('a')}</div>
    <div id="btn-b" class="cb shape-circle" style="left: 422px; top: 150px; width: 46px; height: 46px;" data-key="b" onclick="handleButtonClick('b', '${l('b')}')">${l('b')}</div>
    <div id="btn-rt" class="cb shape-circle" style="left: 474px; top: 132px; width: 46px; height: 46px;" data-key="rt" onclick="handleButtonClick('rt', '${l('rt')}')">${l('rt')}</div>

    <!-- 右端の縦長ボタン (RS) -->
    <div id="btn-rs" class="cb shape-pill-vert" style="left: 536px; top: 120px; width: 52px; height: 86px;" data-key="rs" onclick="handleButtonClick('rs', '${l('rs')}')">${l('rs')}</div>
</div>
`;
}