/* Scalar teaching examples. No expression evaluation, product calls or state changes. */
(() => {
  const types = {};
  const p = (key, label, unit, value, min = 0, integer = false, max = 1e12) => ({ key, label, unit, value, min, integer, max });
  const positive = (key, label, unit, value) => p(key, label, unit, value, 0.000001);
  const signed = (key, label, unit, value) => p(key, label, unit, value, -1e12);
  const count = (key, label, value, min = 1) => p(key, label, 'шт.', value, min, true, 1e9);
  const define = (id, title, params, run, explore = params[0].key, note = '') => { types[id] = { title, params, run, explore, note }; };
  const fmt = value => {
    if (!Number.isFinite(value)) throw new Error('Результат выходит за допустимый численный диапазон.');
    return value !== 0 && Math.abs(value) < 1e-6 ? value.toExponential(4) : value.toLocaleString('ru-RU', { maximumFractionDigits: 6 });
  };
  const line = (expression, value, unit = '') => `${expression} = ${fmt(value)}${unit ? ' ' + unit : ''}`;
  const done = (steps, label, value, unit = '', numeric = {}) => ({ steps, result: `${label} = ${fmt(value)}${unit ? ' ' + unit : ''}`, numeric: { value, ...numeric } });
  const require = (condition, message) => { if (!condition) throw new Error(message); };
  const radians = degrees => degrees * Math.PI / 180;

  // Exact decimals are needed where ceil/floor or money rounding changes a result.
  const rational = raw => {
    const match = String(raw).trim().match(/^([+-]?)(\d*)(?:\.(\d*))?(?:e([+-]?\d+))?$/i);
    require(match && (match[2] || match[3]) && String(raw).length <= 80, 'Введите конечное десятичное число.');
    const exponent = Number(match[4] || 0);
    require(Math.abs(exponent) <= 30, 'Для этого примера используйте обычную десятичную запись.');
    let n = BigInt((match[1] === '-' ? '-' : '') + ((match[2] || '0') + (match[3] || '')));
    let d = 10n ** BigInt((match[3] || '').length);
    if (exponent >= 0) n *= 10n ** BigInt(exponent); else d *= 10n ** BigInt(-exponent);
    return { n, d };
  };
  const r = value => rational(String(value));
  const add = (a, b) => ({ n: a.n*b.d+b.n*a.d, d: a.d*b.d });
  const sub = (a, b) => ({ n: a.n*b.d-b.n*a.d, d: a.d*b.d });
  const mul = (a, b) => ({ n: a.n*b.n, d: a.d*b.d });
  const div = (a, b) => { require(b.n !== 0n, 'Знаменатель не может быть равен нулю.'); return { n: a.n*b.d, d: a.d*b.n }; };
  const decimal = a => Number(a.n) / Number(a.d);
  const floor = a => a.n >= 0n ? a.n/a.d : -((-a.n+a.d-1n)/a.d);
  const ceil = a => -floor({ n: -a.n, d: a.d });
  const money = a => {
    require(a.n >= 0n && a.d > 0n, 'Начисление должно быть неотрицательным.');
    const cents = (2n*a.n*100n+a.d)/(2n*a.d);
    const text = `${cents/100n}.${String(cents%100n).padStart(2, '0')}`;
    return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(text);
  };

  define('cylinder', 'Объём цилиндра', [positive('D','Диаметр','мм',50), positive('L','Длина','мм',100)], x => done([`V = π × ${fmt(x.D)}² × ${fmt(x.L)} / 4`], 'V', Math.PI*x.D*x.D*x.L/4, 'мм³'));
  define('frustum', 'Объём усечённого конуса', [positive('D1','Первый диаметр','мм',80), p('D2','Второй диаметр','мм',40), positive('L','Осевая длина','мм',100)], x => done([`V = π × ${fmt(x.L)} × (${fmt(x.D1)}² + ${fmt(x.D1)} × ${fmt(x.D2)} + ${fmt(x.D2)}²) / 12`], 'V', Math.PI*x.L*(x.D1*x.D1+x.D1*x.D2+x.D2*x.D2)/12, 'мм³'));
  define('mass', 'Перевод объёма и масса', [p('V','Объём','мм³',1000000), positive('rho','Плотность','кг/м³',7850)], x => done([line('V / 10⁹',x.V/1e9,'м³'), `m = ${fmt(x.V/1e9)} × ${fmt(x.rho)}`], 'm',x.V*x.rho/1e9,'кг',{cubicMeters:x.V/1e9}), 'V', 'Плотность здесь является учебным входом, её можно изменить.');
  define('limits', 'Пределы и середина допуска', [positive('nominal','Номинал','мм',50), signed('lower','Нижнее отклонение','мм',-0.3), signed('upper','Верхнее отклонение','мм',-0.1)], x => {
    require(x.lower <= x.upper, 'Нижнее отклонение не должно превышать верхнее.');
    require(x.nominal+x.lower > 0, 'Нижний предел размера должен быть положительным.');
    return done([line('x_min = номинал + нижнее отклонение',x.nominal+x.lower,'мм'),line('x_max = номинал + верхнее отклонение',x.nominal+x.upper,'мм'),line('T = верхний предел − нижний предел',x.upper-x.lower,'мм')], 'Средняя цель',x.nominal+(x.lower+x.upper)/2,'мм',{lower:x.nominal+x.lower,upper:x.nominal+x.upper});
  });
  define('external', 'Требуемый наружный размер', [positive('D','Номинал детали','мм',50), signed('upper','Верхнее отклонение','мм',0.1), p('allowance','Полный припуск на диаметр','мм',2)], x => { require(x.D+x.upper+x.allowance>0,'Требуемый размер должен быть положительным.'); return done([`D_r = ${fmt(x.D)} + (${fmt(x.upper)}) + ${fmt(x.allowance)}`],'D_r',x.D+x.upper+x.allowance,'мм'); });
  define('stock-minimum', 'Гарантированный минимум проката', [positive('D','Номинал проката','мм',82), signed('lower','Нижнее отклонение','мм',-0.8)], x => { require(x.D+x.lower>0,'Минимальный диаметр должен быть положительным.'); return done([`D_min = ${fmt(x.D)} + (${fmt(x.lower)})`],'D_min',x.D+x.lower,'мм'); });
  define('curvature', 'Условный экран по кривизне', [positive('D','Номинал проката','мм',82), signed('lower','Нижнее отклонение','мм',-0.8), positive('L','Выделенная длина','мм',300), p('K','Норма кривизны','%',0.25), positive('required','Требуемый диаметр','мм',80)], (x,raw) => {
    const effective = sub(add(rational(raw.D),rational(raw.lower)),div(mul(rational(raw.L),rational(raw.K)),r(100)));
    const difference = sub(effective,rational(raw.required));
    return { steps:[line('Поправка = L × K / 100',x.L*x.K/100,'мм'),line('D_eff = D + δ − поправка',decimal(effective),'мм'),line('D_eff − D_r',decimal(difference),'мм')], result:difference.n>0n ? 'Учебное условие D_eff > D_r выполнено' : 'Учебное условие D_eff > D_r не выполнено', numeric:{effective:decimal(effective),passes:difference.n>0n} };
  }, 'L', 'Строгое неравенство: равенство не проходит. Эта оценка не является измерением конкретного прутка.');
  define('allowance', 'Радиальный запас', [positive('stock','Минимальный диаметр проката','мм',52), positive('part','Верхний предел детали','мм',50.1)], x => done([`z = (${fmt(x.stock)} − ${fmt(x.part)}) / 2`],'z', (x.stock-x.part)/2,'мм'), 'stock');
  define('cut-length', 'Длина отрезанной заготовки', [positive('L','Длина детали по принятой базе','мм',200), p('left','Левый припуск','мм',2), p('right','Правый припуск','мм',3)], x => done([`L_r = ${fmt(x.L)} + ${fmt(x.left)} + ${fmt(x.right)}`],'L_r', x.L+x.left+x.right,'мм'));
  define('cut-stop', 'Упор и резерв реза', [positive('L','Минимальная длина','мм',203.2), p('minus','Минусовая погрешность, модуль','мм',0.4), p('plus','Плюсовая погрешность, модуль','мм',0.6), p('step','Шаг упора, 0 = неприменим','мм',1)], (x,raw) => {
    const need = add(rational(raw.L),rational(raw.minus));
    const target = x.step === 0 ? need : mul({ n:ceil(div(need,rational(raw.step))), d:1n },rational(raw.step));
    return done([line('L_r + ε_minus',decimal(need),'мм'),line('L_target',decimal(target),'мм')], 'L_allocated',decimal(add(target,rational(raw.plus))),'мм');
  });
  define('capacity', 'Вместимость конечного прутка', [positive('L','Доступная длина прутка','мм',6000), p('head','Тело начального обрезка','мм',10), count('heads','Начальные резы',1,0), p('tail','Минимальный хвост зажима','мм',100), positive('piece','Выделенная длина отрезка','мм',205), positive('kerf','Ширина пропила','мм',3)], (x,raw) => {
    const usable = sub(sub(sub(rational(raw.L),rational(raw.head)),mul(rational(raw.heads),rational(raw.kerf))),rational(raw.tail));
    const pitch = add(rational(raw.piece),rational(raw.kerf));
    const capacity = Number(floor(div(usable,pitch)));
    require(Number.isSafeInteger(capacity), 'Для этого учебного примера число отрезков слишком велико.');
    return done([line('Длина после начальных потерь и хвоста',decimal(usable),'мм'),line('Шаг расхода = отрезок + пропил',decimal(pitch),'мм'),`c = max(0, floor(${fmt(decimal(usable))} / ${fmt(decimal(pitch))}))`], 'c', Math.max(0,capacity),'шт.');
  }, 'piece');
  define('bars', 'Число одинаковых прутков', [count('N','Количество отрезков',20),count('capacity','Вместимость одного прутка',9)], x => done([`B = ceil(${x.N} / ${x.capacity})`],'B',Number(ceil(div(r(x.N),r(x.capacity)))),'прутков'));
  define('rpm', 'Обороты по скорости резания', [positive('D','Опорный диаметр','мм',80),positive('v','Скорость резания','м/мин',120)], x => done([`n = 1000 × ${fmt(x.v)} / (π × ${fmt(x.D)})`],'n',1000*x.v/(Math.PI*x.D),'об/мин'));
  define('speed', 'Скорость по оборотам', [positive('D','Опорный диаметр','мм',80),positive('n','Обороты','об/мин',500)], x => done([`v = π × ${fmt(x.D)} × ${fmt(x.n)} / 1000`],'v',Math.PI*x.D*x.n/1000,'м/мин'));
  define('feed', 'Минутная подача', [positive('n','Обороты','об/мин',500),positive('f','Подача на оборот','мм/об',0.2)], x => done([`u = ${fmt(x.n)} × ${fmt(x.f)}`],'u',x.n*x.f,'мм/мин'), 'n');
  define('tooth-feed', 'Подача фрезы', [positive('n','Обороты','об/мин',1000),count('z','Эффективные зубья',4),positive('fz','Подача на зуб','мм/зуб',0.05)], x => done([`u = ${fmt(x.n)} × ${x.z} × ${fmt(x.fz)}`],'u',x.n*x.z*x.fz,'мм/мин'), 'n');
  define('travel', 'Путь повторяемых движений', [p('L','Путь одного движения','мм',100),count('k','Число повторов',4)], x => done([`L_total = ${fmt(x.L)} × ${x.k}`],'L_total',x.L*x.k,'мм'), 'k');
  define('motion-time', 'Время объявленного движения', [p('L','Полный путь движения','мм',100),positive('u','Подача вдоль пути','мм/мин',100)], x => done([`t = ${fmt(x.L)} / ${fmt(x.u)}`],'t',x.L/x.u,'мин'), 'L');
  define('chip', 'Толщина несрезанной стружки', [positive('f','Подача на оборот','мм/об',0.2),p('angle','Главный угол в плане','град',75,0.001,false,90)], x => done([`h = ${fmt(x.f)} × sin(${fmt(x.angle)} × π / 180)`],'h',x.f*Math.sin(radians(x.angle)),'мм'));
  define('specific-force', 'Удельная сила по модели', [positive('kc11','Коэффициент kc11','Н/мм²',2000),p('m','Показатель mc','1',0.25),positive('h','Толщина стружки','мм',0.2),p('gamma','Передний угол','град',0,-89.999,false,89.999)], x => done([`kc = ${fmt(x.kc11)} × ${fmt(x.h)}^(−${fmt(x.m)}) × (1 − ${fmt(x.gamma)}/100)`],'kc',x.kc11*x.h**(-x.m)*(1-x.gamma/100),'Н/мм²'), 'h', 'Коэффициенты здесь заданы для учебной подстановки, материалу они автоматически не назначаются.');
  define('force', 'Касательная сила', [positive('kc','Удельная сила','Н/мм²',2500),p('a','Радиальная глубина','мм',2),positive('f','Подача на оборот','мм/об',0.2)], x => done([`F = ${fmt(x.kc)} × ${fmt(x.a)} × ${fmt(x.f)}`],'F',x.kc*x.a*x.f,'Н'), 'a');
  define('power', 'Полезная мощность', [p('F','Касательная сила','Н',1000),p('v','Средняя скорость','м/мин',120)], x => done([`P = ${fmt(x.F)} × ${fmt(x.v)} / 60000`],'P',x.F*x.v/60000,'кВт'));
  define('torque', 'Момент по мощности', [p('P','Полезная мощность','кВт',2),positive('n','Обороты','об/мин',500)], x => done([`T = ${fmt(x.P)} × 30000 / (π × ${fmt(x.n)})`],'T',x.P*30000/(Math.PI*x.n),'Н·м'));
  define('drive-power', 'Мощность привода с КПД', [p('P','Полезная мощность','кВт',2),p('eta','КПД, доля единицы','1',0.8,0.000001,false,1)], x => done([`P_drive = ${fmt(x.P)} / ${fmt(x.eta)}`],'P_drive',x.P/x.eta,'кВт'), 'P');
  const turning = x => { require(2*x.a<=x.D,'Удвоенная радиальная глубина не может превышать исходный диаметр.'); return { d:x.D-2*x.a, A:Math.PI*x.a*(x.D-x.a) }; };
  define('turned-diameter', 'Диаметр после слоя', [positive('D','Исходный диаметр','мм',80),p('a','Радиальная глубина','мм',2)], x => done([`d = ${fmt(x.D)} − 2 × ${fmt(x.a)}`],'d',turning(x).d,'мм'));
  define('longitudinal-volume', 'Новый продольный слой', [positive('D','Исходный диаметр','мм',80),p('a','Радиальная глубина','мм',2),p('L','Длина контакта','мм',100)], x => { const z=turning(x); return done([line('d = D − 2a',z.d,'мм'),line('A = πa(D − a)',z.A,'мм²')],'V = A × L',z.A*x.L,'мм³'); });
  define('longitudinal-rate', 'Производительность продольного слоя', [positive('D','Исходный диаметр','мм',80),p('a','Радиальная глубина','мм',2),positive('u','Минутная подача','мм/мин',100)], x => { const z=turning(x); return done([line('A = πa(D − a)',z.A,'мм²'),`Q = ${fmt(z.A)} × ${fmt(x.u)} / 1000`],'Q',z.A*x.u/1000,'см³/мин'); });
  define('facing', 'Торцевой слой и рабочий ход', [positive('D','Наружный диаметр','мм',80),p('d','Внутренний диаметр','мм',0),p('a','Осевой слой','мм',1),positive('u','Радиальная подача','мм/мин',100)], x => {
    require(x.d<x.D,'Внутренний диаметр должен быть меньше наружного.');
    const L=(x.D-x.d)/2,V=Math.PI*(x.D-x.d)*(x.D+x.d)*x.a/4,t=L/x.u;
    return done([line('L = (D − d)/2',L,'мм'),line('V = π(D² − d²)a/4',V,'мм³'),line('t = L/u',t,'мин')],'Q = V/(1000t)',V/(1000*t),'см³/мин',{L,V,t});
  });
  define('boring', 'Новый кольцевой объём расточки', [positive('d0','Диаметр до расточки','мм',20),positive('d1','Диаметр после расточки','мм',24),p('L','Длина контакта','мм',50)], x => {
    require(x.d1>=x.d0,'При расточке конечный диаметр не меньше начального.');
    const A=Math.PI*(x.d1-x.d0)*(x.d1+x.d0)/4;
    return done([line('a = (d1 − d0)/2',(x.d1-x.d0)/2,'мм'),line('A = π(d1² − d0²)/4',A,'мм²')],'V = A × L',A*x.L,'мм³',{a:(x.d1-x.d0)/2,A});
  }, 'L');
  define('drill-tip', 'Цилиндрическая глубина и вершина', [positive('D','Диаметр сверла','мм',20),p('H','Глубина полного цилиндра','мм',50),p('angle','Полный угол вершины','град',118,0.001,false,179.999)], x => { const tip=x.D/(2*Math.tan(radians(x.angle)/2)); return done([line('h_tip = D/(2 tan(θπ/360))',tip,'мм')],'Глубина до вершины = H + h_tip',x.H+tip,'мм',{tip}); }, 'D');
  define('saw', 'Один рез круглого прутка', [positive('D','Диаметр','мм',75),positive('R','Площадная производительность','см²/мин',20),positive('k','Пропил','мм',3)], x => {
    const A=Math.PI*x.D*x.D/4,t=A/(100*x.R);
    return done([line('A = πD²/4',A,'мм²'),line('A / 100',A/100,'см²'),line('V_kerf = A × k',A*x.k,'мм³'),line('Q_kerf = R × k/10',x.R*x.k/10,'см³/мин')],'t = A/(100R)',t,'мин',{A,volume:A*x.k,rate:x.R*x.k/10});
  });
  define('thread', 'Время однозаходной резьбы резцом', [positive('P','Шаг','мм',2),positive('n','Обороты','об/мин',300),p('L','Осевой рабочий путь','мм',40)], x => done([line('u = nP',x.n*x.P,'мм/мин')],'t = L/(nP)',x.L/(x.n*x.P),'мин',{feed:x.n*x.P}), 'L', 'Только рабочий осевой ход. Этот пример не рассчитывает точный винтовой объём cut-хода.');
  define('lead', 'Ход многозаходной резьбы', [positive('P','Шаг','мм',2),count('starts','Число заходов',1)], x => done([`f = ${fmt(x.P)} × ${x.starts}`],'f',x.P*x.starts,'мм/об'), 'starts');
  define('inclined-path', 'Длина наклонной образующей', [p('Z','Осевой пролёт','мм',100),signed('deltaD','Разность диаметров концов','мм',20)], x => done([line('Изменение радиуса = ΔD/2',x.deltaD/2,'мм'),`L = √(${fmt(x.Z)}² + (${fmt(x.deltaD)}/2)²)`],'L',Math.hypot(x.Z,x.deltaD/2),'мм'),'Z');
  define('grinding-stroke', 'Размах продольного хода круга', [positive('L','Длина зоны','мм',100),positive('B','Ширина круга','мм',20),p('low','Левый перебег','мм',5),p('high','Правый перебег','мм',5)], x => {
    require(x.L-x.B+x.low+x.high>=0,'Получается отрицательный продольный ход: проверьте ширину круга и перебеги.');
    return done([line('X_low = B/2 − e_low',x.B/2-x.low,'мм'),line('X_high = L − B/2 + e_high',x.L-x.B/2+x.high,'мм')],'S = L − B + e_low + e_high',x.L-x.B+x.low+x.high,'мм',{low:x.B/2-x.low,high:x.L-x.B/2+x.high});
  });
  define('batch-time', 'Наладка, партия и удельное время', [p('setup','Наладка на партию','мин',30),p('piece','Повторяемое время детали','мин',6),count('N','Детали в партии',20)], x => done([line('N × t_piece',x.N*x.piece,'мин'),line('T_batch = T_setup + N × t_piece',x.setup+x.N*x.piece,'мин')],'Удельное время = T_batch/N',x.piece+x.setup/x.N,'мин/дет.'), 'N');
  define('inspection', 'Выборка и время контроля', [count('N','Детали в партии',23),p('percent','Выборка','%',10,0,false,100),p('duration','Время одной проверки','мин',2)], (x,raw) => { const exact=div(mul(rational(raw.N),rational(raw.percent)),r(100)),n=Number(ceil(exact)); return done([line('N × p/100',decimal(exact),'проверок'),line('Число проверок с округлением вверх',n,'шт.')],'Время ОТК',n*x.duration,'мин',{count:n}); },'N','Для учебного примера явно выбрано правило округления ceil.');
  define('labor', 'Коэффициент выбранной трудоёмкости', [p('base','Исходное время','мин',10),p('selected','Выбранная часть времени','мин',4),p('K','Коэффициент','1',1.5,1)], x => { require(x.selected<=x.base,'Выбранная часть не может превышать базовое время.'); return done([line('Добавка = t_selected × (K − 1)',x.selected*(x.K-1),'мин')],'Новое время',x.base+x.selected*(x.K-1),'мин'); },'K');
  define('hour-cost', 'Начисление по часовой ставке', [p('minutes','Начисляемое время','мин',12),p('rate','Учебная часовая ставка','₽/ч',1000)], (x,raw) => {
    const amount=div(mul(rational(raw.minutes),rational(raw.rate)),r(60));
    return {steps:[`C = ${fmt(x.minutes)} × ${fmt(x.rate)} / 60`,line('До денежного округления',decimal(amount),'₽')],result:`C = ${money(amount)}`,numeric:{value:decimal(amount)}};
  },'minutes','Округление RUB до копеек выполняется по правилу half-up. Ставка является учебным значением.');
  define('unit-cost', 'Цена единицы и количество', [p('price','Цена единицы','₽/ед.',100),p('quantity','Количество единиц','ед.',20)], (x,raw) => {
    const amount=mul(rational(raw.price),rational(raw.quantity));
    return {steps:[`C = ${fmt(x.price)} × ${fmt(x.quantity)}`],result:`C = ${money(amount)}`,numeric:{value:decimal(amount)}};
  },'quantity','Стоимость одной строки округляется до копеек; это учебное начисление.');

  function evaluate(kind, raw) {
    const config = types[kind];
    require(Boolean(config),'Неизвестный учебный пример.');
    const x = {};
    for (const field of config.params) {
      require(raw[field.key] !== undefined && String(raw[field.key]).trim() !== '', `UNKNOWN: заполните поле «${field.label}».`);
      const value = Number(raw[field.key]);
      require(Number.isFinite(value) && value>=field.min && value<=field.max, `Поле «${field.label}»: допустимо от ${field.min} до ${field.max}.`);
      require(!field.integer || Number.isSafeInteger(value), `Поле «${field.label}» должно быть целым.`);
      x[field.key] = value;
    }
    const result = config.run(x,raw);
    for (const value of Object.values(result.numeric || {})) require(typeof value !== 'number' || Number.isFinite(value),'Не удалось получить конечный результат.');
    return result;
  }
  globalThis.MetallLearning = { types, evaluate };
  if (typeof document === 'undefined') return;
  const escape = value => String(value).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function initialize(panel) {
    if (panel.dataset.initialized) return;
    panel.dataset.initialized = 'true';
    const config = types[panel.dataset.example], container = panel.querySelector('.learning-content'), prefix = panel.id;
    container.innerHTML = `<p class="learning-caption">Измените значения: подстановка и результат пересчитываются сразу.</p><div class="learning-layout"><div class="learning-inputs"><div class="learning-fields">${config.params.map(field=>`<div class="field"><label for="${prefix}-${field.key}">${escape(field.label)}${field.unit==='1'?'':', '+escape(field.unit)}</label><input id="${prefix}-${field.key}" name="${prefix}-${field.key}" data-key="${field.key}" type="number" min="${field.min}" max="${field.max}" step="${field.integer?'1':'any'}" value="${field.value}" aria-describedby="${prefix}-error"></div>`).join('')}</div><div class="learning-controls"><button type="button" data-action="double" class="button-primary">Удвоить: ${escape(config.params.find(p=>p.key===config.explore).label.toLocaleLowerCase('ru'))}</button><button type="button" data-action="reset">Исходный пример</button></div><p class="learning-error" id="${prefix}-error" role="status" aria-live="polite"></p></div><div class="learning-solution"><p class="learning-label">Результат</p><output class="learning-result" aria-label="Результат расчёта" aria-live="polite"></output><p class="learning-label">Подстановка</p><ol class="learning-steps"></ol></div></div>${config.note?`<p class="learning-note">${escape(config.note)}</p>`:''}<p class="learning-note">Учебная подстановка не меняет статус метода и исходные данные Metall.</p>`;
    const inputs = [...container.querySelectorAll('input')], output=container.querySelector('output'), error=container.querySelector('.learning-error'), steps=container.querySelector('.learning-steps');
    function update() {
      const raw = Object.fromEntries(inputs.map(input=>[input.dataset.key,input.value]));
      inputs.forEach(input=>input.setAttribute('aria-invalid',String(input.value==='' || !input.validity.valid)));
      try {
        const result=evaluate(panel.dataset.example,raw);
        error.textContent=''; steps.replaceChildren(...result.steps.map(text=>{const item=document.createElement('li');item.textContent=text;return item;}));
        output.classList.remove('is-unknown');
        output.textContent=panel.dataset.primary ? JSON.parse(panel.dataset.primary).map(([key,label,unit])=>`${label} = ${fmt(result.numeric[key])} ${unit}`).join('; ') : result.result;
      } catch (problem) { error.textContent=problem.message;output.textContent='UNKNOWN';output.classList.add('is-unknown');steps.replaceChildren(); }
    }
    inputs.forEach(input=>input.addEventListener('input',update));
    container.querySelector('[data-action="reset"]').addEventListener('click',()=>{inputs.forEach(input=>input.value=config.params.find(field=>field.key===input.dataset.key).value);update();});
    container.querySelector('[data-action="double"]').addEventListener('click',()=>{const input=inputs.find(input=>input.dataset.key===config.explore);if(input.value!=='')input.value=String(Number(input.value)*2);update();});
    update();
  }
  document.querySelectorAll('.learning-example').forEach(initialize);
})();
