const actions = [
    "I choked on",
    "I got face fucked by",
    "I sucked and gagged on filthy big white cock",
    "I sucked and gagged on filthy big black cock",
    "I sucked on balls",
    "I sucked on balls that teabagged me",
    "I love sucking dick",
    "I love sucking cock",
    "I love spreading my asshole for big black cock",
    "I love spreading my butthole for big white cock",
    "I love spreading my asshole and stretching it out",
    "I got gangbanged by",
    "I got smacked by",
    "I gagged on",
    "I drained",
    "I was put upside down and face fucked by",
    "I got fucked in",
    "I swallowed cum from",
    "I took that heavy bbc in",
    "spread my cheeks wide for",
    "got stretched out by",
    "begged for more bbc inside",
    "rode cowgirl on",
    "rode reverse cowgirl on"
];

const subjects = [
    "that big black cock",
    "that throbbing bbc",
    "that massive big black cock",
    "that heavy bbc",
    "that monster cock",
    "that massive big white cock",
    "that thick bwc",
    "that throbbing white dick",
    "that heavy white shaft",
    "an enormous BBC",
    "a fat veiny dick"
];

const contexts = [
    "until tears streamed down my face.",
    "while getting drilled from behind at the truck-stop gloryhole.",
    "like a desperate slut at the rest-stop bathroom.",
    "until my jaw locked completely.",
    "while my gaping asshole was getting wrecked.",
    "like a pathetic sissy with cumswapping dripping everywhere.",
    "until my loose hole leaked thick ropes.",
    "while being filmed by strangers in the public restroom.",
    "until warm cum filled my throat and bubbled out my nose.",
    "while crying on the dirty bathroom floor.",
    "until thick cum poured from my gaping asshole and winking butthole.",
    "leaving a puddle of jizz on my stretched butthole.",
    "while getting pounded deep in my ass with intense cumswapping.",
    "with cumshots all over my face while I eagerly licked it off."
];

const names = ["Ashley", "Trina", "Chloe", "Brittany", "Jessica", "Tiffany", "Amber", "Samantha", "Destiny", "Candy", "Lexi", "Chanel", "Nikki", "Savannah", "Zoe"];
const titles = ["Mistress", "Slut", "Sissy", "Bimbo", "Prostitute", "Trans-whore", "Cumdump", "Whore", "Slut-puppet"];

function getRandomItem(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function generatePhrases(count) {
    const phrases = [];
    const seen = new Set();
    let tries = 0;
    const maxTries = count * 40;

    while (phrases.length < count && tries < maxTries) {
        tries++;
        const act = getRandomItem(actions);
        const subj = getRandomItem(subjects);
        const ctx = getRandomItem(contexts);
        const num = Math.random() > 0.4 ? Math.floor(Math.random() * 10) + 1 : null;

        let p = "";
        if (act.includes("smacked by") && num) {
            p = `${act} ${num} dicks and then gangbanged by ${num} guys ${ctx}`;
        } else if (act.includes("gangbanged by") && num) {
            p = `${act} ${num} horny strangers in the truck-stop stall ${ctx}`;
        } else if (act.includes("drained") && num) {
            p = `I drained ${num} guys at the glory hole ${ctx}`;
        } else if (act.includes("gagged on") && num) {
            p = `I gagged on ${num} dicks and swallowed cum like a cum guzzling whore ${ctx}`;
        } else if (act.includes("fucked in")) {
            const hole = getRandomItem(["my ass", "my asshole", "my butthole", "my gaping asshole"]);
            p = `${act} ${hole} by ${subj} ${ctx}`;
        } else {
            p = `${act} ${subj} ${ctx}`;
        }

        if (!seen.has(p)) {
            seen.add(p);
            phrases.push(p);
        }
    }

    document.getElementById('itemCountBadge').textContent = `${phrases.length} items`;
    return phrases.map((p, i) => `${i + 1}. ${p}`).join("\n");
}

function generateStory() {
    const name = getRandomItem(names);
    const title = getRandomItem(titles);
    const persona = `${title} ${name}`;

    const stories = [
        `=== Story: The Birthday Gangbang (${persona}) ===\n\n${persona} stood in the center of the crowded party room wearing only a collar, bent over the kitchen island with a giant frosted birthday cake and cupcakes resting right on her lower back and gaping asshole. 'It's time for the birthday cum-cake,' one of the guys laughed. With 8 horny strangers lined up, ${persona} loved spreading her asshole and stretching it out for every big black cock and big white cock in the room.\n\nShe got gangbanged by 8 guys in rapid succession, riding reverse cowgirl while choking on successive dicks. As each man pulled out, they swapped cum directly into her mouth in a wild session of cumswapping. Finally, the frosting on the birthday cake and cupcakes was completely buried under thick, warm ropes of cum, which she eagerly lapped up like a true cum-guzzling whore.`,
        
        `=== Story: Upside-Down Torture (${persona}) ===\n\nSuspended upside down by her ankles in the truck-stop backroom, ${persona} was helpless as she was put upside down and face fucked by different men while spit ran down her face and tears came out. Her jaw locked repeatedly, but she sucked and gagged on filthy big white cock and big black cock without mercy. With her mind melting from sensory overload, a random stranger girl she didn't know—along with a local sissy and a tattooed bimbo—took turns letting ${persona} drink fresh, warm cum straight from their dripping buttholes.\n\nShe coughed, gagged on 6 dicks, and swallowed every last drop of the cumswapped mess, her gaping asshole pulsing and leaking onto the dirty floor below.`,

        `=== Story: The Gloryhole Marathon (${persona}) ===\n\nLocked inside the grimy rest-stop bathroom stall, ${persona} opened her mouth wide at the wall opening. She got smacked by 7 dicks and then gangbanged by 7 guys in a brutal relay race. She loved spreading her butthole for big black cock and big white cock, letting each stranger redefine the limits of her gaping asshole.\n\nDrained and completely used up, she rode cowgirl on the last heavy shaft, letting cum drip out of her stretched-out hole while she licked cumshots off her own face.`
    ];

    document.getElementById('itemCountBadge').textContent = `1 story`;
    return getRandomItem(stories);
}

document.getElementById('modeSelect').addEventListener('change', function() {
    const countGroup = document.getElementById('countGroup');
    if (this.value === 'story') {
        countGroup.style.display = 'none';
    } else {
        countGroup.style.display = 'flex';
    }
});

document.getElementById('generateBtn').addEventListener('click', function() {
    const mode = document.getElementById('modeSelect').value;
    const outputContainer = document.getElementById('outputContainer');
    const copyBtn = document.getElementById('copyBtn');

    let result = '';
    if (mode === 'phrases') {
        const count = parseInt(document.getElementById('countInput').value) || 50;
        result = generatePhrases(count);
    } else {
        result = generateStory();
    }

    outputContainer.textContent = result;
    copyBtn.style.display = 'block';
});

document.getElementById('copyBtn').addEventListener('click', function() {
    const outputText = document.getElementById('outputContainer').textContent;
    navigator.clipboard.writeText(outputText).then(() => {
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<span>Copied Successfully!</span>';
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
        }, 2000);
    });
});
