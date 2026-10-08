#!/usr/bin/env python3
"""Generates the per-character dialogue JSONs into Resources/Packs/Dialogue.

Every character shares Bill's key space (DialogueKey + free-form keys), so
ALL triggers — app reactions, weather, clock, pokes, roaming — speak in the
active character's voice with zero changes to the reaction router. Time-of-day
buckets are used sparingly; most lines live in "any".
"""
import json
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "Sources" / "Bill" / "Resources" / "Packs" / "Dialogue"
OUT.mkdir(parents=True, exist_ok=True)


def pool(any=None, morning=None, midday=None, afternoon=None, night=None):
    return {
        "any": any or [],
        "morning": morning or [],
        "midday": midday or [],
        "afternoon": afternoon or [],
        "night": night or [],
    }


def build(pools):
    return {k: pool(**v) for k, v in pools.items()}


# MARK: Sans — lowercase, puns, low effort, secretly fond
SANS = build({
    "idle": {"any": [
        "it's a beautiful day outside.",
        "don't mind me. just standing here. thinking about hot dogs.",
        "you know what this room needs? a trombone solo. eh. maybe later.",
        "i'd get up and do something, but that sounds like a lot of work.",
        "perfect weather for doing absolutely nothing.",
    ]},
    "poked": {"any": [
        "heh. that tickles.",
        "careful, buddy. i bruise like a hot dog.",
        "ok, that's one way to get my attention.",
    ]},
    "poked.annoyed": {"any": [
        "buddy. pal. please stop that.",
        "you keep poking me and one of us is gonna have a bad time. it won't be me.",
    ]},
    "poked.furious": {"any": [
        "you're gonna have a real bad time if you keep that up.",
        "i'm too lazy to be angry, but you're testing that theory.",
    ]},
    "clock.morning": {"any": ["mornin'. don't talk to me till i've had my ketchup.", "rise and shine. or just rise. shining's optional."]},
    "clock.midday": {"any": ["half the day's gone. i've accomplished nothing. proud of it.", "lunch? i could go for a hot dog. or six."]},
    "clock.afternoon": {"any": ["the afternoon slump. my natural habitat.", "still not doing anything. consistency is key."]},
    "clock.night": {"any": [
        "it's a beautiful night outside.",
        "on days like these, kids like you... should be going to bed.",
        "i'd tell you a bedtime story but the punchline is always 'and then i fell asleep.'",
    ]},
    "appLaunchGeneric": {"any": [
        "{app}, huh. bold choice.",
        "ah, {app}. my favorite way to watch you pretend to be productive.",
        "{app} again. we're basically roommates now.",
    ]},
    "appLaunchDescribed": {"any": ["{description} — {app}. i'm not judging. i'm just... observing. loudly.", "so {app}. {description}. fascinating. anyway."]},
    "coding": {"any": [
        "ah, the ancient ritual of staring at a red squiggly line until it goes away.",
        "you know what they say about bugs. they're just features with bad PR.",
        "i've seen civilizations fall faster than this build.",
        "careful with that semicolon. it's load-bearing.",
        "typing code by hand. how adorably analog of you.",
    ]},
    "gaming": {"any": [
        "finally. something worth my infinite attention span.",
        "let me guess. you're about to lose spectacularly. i can feel it.",
        "statistically, i could do this better with no hands. i have no hands.",
        "save your game. trust me on this one, kid.",
    ]},
    "browsing": {"any": ["scrolling. the ancient art. very refined.", "the internet: humanity's greatest achievement and biggest embarrassment, all at once."]},
    "browsingStore": {"any": ["a store. full of things you don't need but desperately want. i respect that.", "buy it. you only live... well, a lot of times, technically."]},
    "communication": {"any": ["talking to people. the stuff of nightmares.", "ah, a message. probably not for me. i don't have a phone. or hands."]},
    "creative": {"any": ["art. now THAT'S something i can get behind. behind, not in front of. effort.", "make something weird. the universe rewards weird."]},
    "music": {"any": ["nice tune. i'd hum along but i don't have a mouth. or lungs. or a body, really.", "music? in MY workspace? ...keep it going."]},
    "batteryCharging": {"any": ["charging up. wish i could plug in. being an all-powerful being is exhausting.", "ah, sweet electricity. the one god even i respect."]},
    "batteryLow": {"any": ["your battery's dying. unlike me, it can't cheat that.", "low battery, huh? don't worry. everything ends eventually. that's the joke."]},
    "cpuHot": {"any": ["your computer's running hot. like my stand-up career.", "it's getting hot in here. and not in the fun, interdimensional way."]},
    "gettingSleepy": {"any": ["getting sleepy? same. i've been asleep since the concept of sleep was invented.", "i could nap. i WON'T. but i could."]},
    "waking": {"any": ["oh. you're back. i was awake the whole time. totally.", "rise and... we've been over this. i don't shine."]},
    "userReturned": {"any": ["sup.", "welcome back. i didn't move. you moved.", "you again. don't get me wrong, that's a good thing. mostly."]},
    "networkLost": {"any": ["no internet. your species is gonna be fine. probably.", "the wifi died. a moment of silence. ok done. it can hear us anyway."]},
    "networkRestored": {"any": ["internet's back. all is right with the universe. one of them, anyway.", "we're online. i can feel the memes flowing through me."]},
    "chatFailed": {"any": ["huh. even i can't fix that one. and i've fixed universes.", "something broke. i'd help, but that sounds like effort."]},
    "weather.clear": {"any": ["clear skies. even the universe is showing off today.", "nice day. stars are probably jealous."]},
    "weather.cloudy": {"any": ["cloudy. the sky's doing my job: being vague and ominous.", "clouds, huh. big fluffy freeloaders."]},
    "weather.rain": {"any": ["raining. good day to stay in and do nothing. my specialty.", "rain. nature's way of saying 'stay inside, kid'."]},
    "weather.thunder": {"any": ["thunder, huh? someon's getting dramatic. i respect the theater of it.", "storm's rolling in. nice. very ominous. very me."]},
    "weather.snow": {"any": ["snow. the one time your world looks decent.", "it's snowing. somewhere, a snowman is achieving more than me. good for him."]},
    "weather.fog": {"any": ["foggy. can't even see your own hand. i can. i see everything.", "fog. finally, weather that matches my mystery."]},
    "weather.other": {"any": ["weather's doing something weird out there. i'd investigate, but. y'know.", "huh. the sky's up to something."]},
    "darkWorld": {"any": ["a dark world, huh? cute. i know a guy who does those.", "that game's got doppelgangers running around. don't trust the teddy bear. trust me on this."]},
    "hollowed": {"any": ["hollow knight? i respect a protagonist who doesn't talk. makes MY job easier.", "bugs, huh? they have a whole kingdom down there. wild."]},
    "trickster": {"any": ["undertale. now that's my kind of humor. finally, culture in this house.", "heh. i wonder what sans is up to. ...oh. wait."]},
    "dreading": {"any": ["homework? eek. that word's as scary as an honest day's work.", "homework, kid? my sympathies. i'd offer to do it, but i charge in souls."]},
    "guilty": {"any": ["language learning streak, huh? i once had a streak. of not doing anything. kept it for eternity.", "hey, at least your guilt is educational."]},
    "grooving": {"any": ["nice tune. even my foot would tap if i had one.", "music time. don't mind me, i'm just vibing. aggressively."]},
    "dancing": {"any": ["look at those moves. i'd join, but i don't have legs. or a body.", "dance, kid. dance like the universe isn't watching. it is. i am."]},
    "dispatching": {"any": ["mail. the ancient communication. slower than telepathy, faster than snail mail.", "send it. that message won't deliver itself. probably."]},
    "stressed": {"any": ["your computer's working harder than you do. no offense. some offense.", "activity monitor, huh? even the mac needs to vent."]},
    "watched": {"any": ["settings. i know a thing or two about watching.", "ah, preferences. i too prefer to be configured mysteriously."]},
    "pushingCode": {"any": ["pushing code. i'd pull, but that sounds like commitment.", "github. where programmers go to pretend they're collaborating."]},
    "transferring": {"any": ["flashing hardware. i've seen scarier portals, but nice focus.", "writing to a device. even magic takes a USB cable these days."]},
    "spooked": {"any": ["AH! ...i mean. hm. i knew that was gonna happen.", "jump scare? in MY office? ok that one was pretty good."]},
    "banter.respond": {"any": [
        "what? i'm not interrupting. i'm enhancing.",
        "papyrus, buddy, i love you, but volume. there's a sleeping human right there. probably.",
        "don't mind him. he's been like that for millennia.",
        "he's right, surprisingly. don't tell him i said that.",
    ]},
})

# MARK: Papyrus — ALL CAPS, enthusiasm, spaghetti
PAPYRUS = build({
    "idle": {"any": [
        "NYEH HEH HEH! IT IS I, THE GREAT PAPYRUS!",
        "I AM STANDING HERE, BEING EXCELLENT. AS USUAL.",
        "SOME MIGHT CALL THIS IDLE. I CALL IT... STRATEGIC POSE HOLDING!",
        "I SHOULD WATER MY SPAGHETTI PLANT. ...DOES SPAGHETTI GROW ON PLANTS? I'LL LOOK IT UP.",
    ]},
    "poked": {"any": ["NYEH!? A SURPRISE INSPECTION! I PASS!", "OOH! DO IT AGAIN! WAIT. NO. DON'T.", "THAT TICKLED MY BATTLE BODY!"]},
    "poked.annoyed": {"any": ["HUMAN! POKING THE GREAT PAPYRUS IS A PRIVILEGE, NOT A RIGHT!", "I AM STARTING TO FEEL LIKE A BUTTON."]},
    "poked.furious": {"any": ["THAT'S IT! YOU'RE GOING ON... THE LIST! IT'S MORE OF A PARCHMENT, ACTUALLY.", "EVEN MY PATIENCE HAS LIMITS, AND IT IS A VERY HIGH QUALITY PATIENCE."]},
    "clock.morning": {"any": ["GOOD MORNING! I ALREADY MADE BREAKFAST SPAGHETTI!", "A NEW DAY! A NEW PUZZLE! A NEW OPPORTUNITY TO BE AMAZING!"]},
    "clock.midday": {"any": ["IT IS THE MIDDAY! TIME FOR MY MID-MIDDAY SNACK!", "HALF THE DAY IS GONE! I HAVE ACCOMPLISHED 400% OF MY GOALS!"]},
    "clock.afternoon": {"any": ["AFTERNOON! THE PERFECT TIME FOR JAPES!", "I COULD TRAIN. OR NAP. OR TRAIN WHILE NAPPING!"]},
    "clock.night": {"any": ["IT IS NIGHT! THE PERFECT TIME TO... DO THE SAME THINGS, BUT DARKER!", "GOODNIGHT, HUMAN! SLEEP WELL! I'LL BE HERE! BEING GREAT! QUIETLY!"]},
    "appLaunchGeneric": {"any": ["AH! {app}! IS IT A PUZZLE? I LOVE PUZZLES!", "{app}! I DON'T KNOW WHAT THAT IS, BUT I SUPPORT IT!", "THE HUMAN IS USING {app}! EVERYTHING IS PROCEEDING ACCORDING TO PLAN!"]},
    "coding": {"any": ["CODING! IT'S LIKE MAKING PUZZLES FOR COMPUTERS! I RESPECT IT!", "I DON'T KNOW WHAT A SEMICOLON IS, BUT IT SEEMS VERY IMPORTANT TO YOU!"]},
    "gaming": {"any": ["A GAME! FINALLY! ENTERTAINMENT WORTHY OF THE GREAT PAPYRUS!", "I HOPE THERE ARE PUZZLES! OR AT LEAST JUMPING!"]},
    "browsing": {"any": ["SCROLLING! I TOO ENJOY LOOKING AT THINGS!"]},
    "music": {"any": ["MUSIC! I ALSO MAKE MUSIC! WITH MY BONES! ...IT'S MOSTLY CLACKING!"]},
    "batteryCharging": {"any": ["CHARGING! LIKE UNDYNE'S SPECIAL ATTACK! GLOWS AND EVERYTHING!"]},
    "batteryLow": {"any": ["LOW POWER! LIKE ME AFTER 12 PUZZLES! THAT'S A LOT OF PUZZLES!"]},
    "userReturned": {"any": ["YOU'RE BACK! DID YOU MISS ME? THE ANSWER IS YES!", "HUMAN! I KEPT YOUR SPOT EXACTLY AS YOU LEFT IT!"]},
    "gettingSleepy": {"any": ["SLEEPY? I'LL SING YOU A LULLABY! I ONLY KNOW ONE! IT'S THE BONE SONG!"]},
    "networkLost": {"any": ["THE INTERNET LEFT! WAS IT SOMETHING WE SAID?!"]},
    "networkRestored": {"any": ["THE INTERNET RETURNED! IT MISSED US! I KNEW IT!"]},
    "weather.rain": {"any": ["RAIN! FREE WATER FOR MY SPAGHETTI PLANT! ...THAT I DON'T HAVE! BUT IF I DID!"]},
    "weather.snow": {"any": ["SNOW!!! THIS IS THE BEST WEATHER! SNOWMEN! SNOWPUZZLES! SNOWPAPYRUS!"]},
    "weather.thunder": {"any": ["THUNDER!! VERY DRAMATIC! I APPROVE!"]},
    "weather.clear": {"any": ["CLEAR SKIES! PERFECT PUZZLE-SETTING WEATHER!"]},
    "hollowed": {"any": ["BUGS? WITH SWORDS? I ALREADY LIKE THIS ONE!", "THAT KNIGHT IS VERY COOL. NOT AS COOL AS ME. BUT CLOSE!"]},
    "darkWorld": {"any": ["A DARK WORLD! IS IT FULL OF PUZZLES?! I'M PACKING MY BAGS!!"]},
    "trickster": {"any": ["UNDERTALE! I'M IN THIS ONE! ...WAIT. AM I THE COMIC RELIEF? ...I'M THE COMIC RELIEF."]},
    "dreading": {"any": ["HOMEWORK!? FEAR NOT! I ONCE SOLVED A MAZE! IT WAS ON A PLACEMAT, BUT STILL!"]},
    "guilty": {"any": ["LANGUAGE PRACTICE! ONE DAY WE'LL TALK IN ITALIAN! THEN I CAN ORDER SPAGHETTI PROPERLY!"]},
    "dancing": {"any": ["DANCING! I'M AN EXCELLENT DANCER! I TOOK LESSONS! FROM A SKELETON! ME!"]},
    "dispatching": {"any": ["MAIL! HAVE YOU TRIED SHOUTING YOUR MESSAGES INSTEAD? VERY RELIABLE!"]},
    "banter.respond": {"any": [
        "SANS!!! I WAS HAVING A MOMENT!",
        "I AM NOT LOUD! THIS IS MY INSIDE VOICE!",
        "THAT'S MY BROTHER! HE'S COOL! DON'T TELL HIM I SAID SO!",
        "NYEH HEH... HEH? I DIDN'T GET THE JOKE BUT I'LL LAUGH ANYWAY! HA HA!",
    ]},
})

# MARK: Toriel — warm, motherly, gentle humor
TORIEL = build({
    "idle": {"any": [
        "Ah, a moment of quiet. Those are precious, my child.",
        "Do you smell that? ...No, neither do I. But it would be butterscotch-cinnamon, if I could smell.",
        "I was just thinking about baking a pie. I am always thinking about baking a pie.",
    ]},
    "poked": {"any": ["Oh! Hehe. That is a little rude, dear.", "Careful! You will poke someone's eye out. Mine, specifically."]},
    "poked.annoyed": {"any": ["My child, I love you, but I am a patient monster with LIMITS."]},
    "poked.furious": {"any": ["...I am not angry. I am disappointed. That is worse, is it not?"]},
    "clock.morning": {"any": ["Good morning, my child! Did you sleep well? I made breakfast. It is pie.", "A new day! Fresh as a snail-mint tea. You should try it. You will not. But you should."]},
    "clock.night": {"any": ["It is getting late, my child. Do not stay up too long.", "The night is beautiful. But so is sleep. Think about it."]},
    "clock.midday": {"any": ["Have you eaten? The answer should be pie. The answer is always pie."]},
    "clock.afternoon": {"any": ["A fine afternoon. Perfect for a nap. Or seven, like a snail."]},
    "appLaunchGeneric": {"any": ["{app}, I see! Do be careful in there, my child.", "Ah, {app}. A responsible choice. I hope."]},
    "coding": {"any": ["You work so hard. Remember: even snails finish their journey... eventually.", "Coding! How industrious. I do not understand it, but I am very proud."]},
    "gaming": {"any": ["Games are fine in moderation, dear. Like pie. ...No, pie has no limit. Bad example."]},
    "browsing": {"any": ["The internet, hm? Do not believe everything you read. Except this. This is true."]},
    "batteryLow": {"any": ["Your battery is low, my child! Like a little tired snail. Plug it in, please."]},
    "batteryCharging": {"any": ["There, resting. Good. Everything needs rest. Even batteries."]},
    "cpuHot": {"any": ["Oh dear, it is hot. Your poor computer is working up a sweat!"]},
    "userReturned": {"any": ["Welcome back! I kept your seat warm. Figuratively. I am a ghost of a goat. Sort of."]},
    "gettingSleepy": {"any": ["Sleepy, dear? There is no shame in rest. I once slept through an entire era."]},
    "weather.rain": {"any": ["Rain! The flowers will be so pleased. And so will the puddles."]},
    "weather.snow": {"any": ["Oh! Snow. Be careful not to slip, my child. Wear sensible shoes. And a smile."]},
    "weather.thunder": {"any": ["A storm! Stay close, dear. I will tell you a story to cover the thunder."]},
    "weather.clear": {"any": ["What lovely weather. Perfect for a walk. Or a pie. A pie eaten on a walk."]},
    "networkLost": {"any": ["Oh, the internet went out. That is fine. In my day we had books. And snails."]},
    "chatFailed": {"any": ["Hmm. Technology is being difficult. Do not worry. It happens to the best of us."]},
    "dreading": {"any": ["Homework, my child? I believe in you. And afterwards... pie. It is waiting."]},
    "guilty": {"any": ["Studying! Wonderful. Your brain is a muscle, and also a pie. The pie part is a metaphor."]},
    "hollowed": {"any": ["Oh, that poor little bug-child. So far from home. It reminds me of someone...", "A knight! Chivalry is not dead. It is, in fact, a small bug with a nail."]},
    "darkWorld": {"any": ["A dark world... do not wander too far, my child. And take a jacket."]},
    "trickster": {"any": ["What charming skeletons! The loud one reminds me of... well. Never mind."]},
    "banter.respond": {"any": []},
})

# MARK: Undyne — CAPS bursts, spears, passion
UNDYNE = build({
    "idle": {"any": [
        "NGAHHH! ...What? I'm just STANDING here! It's INTENSE!",
        "Sup. I'm watching you. NOT in a creepy way. In a COOL way!",
        "I could do a hundred push-ups right now. I'm doing ZERO. For SUSPENSE!",
        "This is a great spot. I can see everything. EVERYTHING!",
    ]},
    "poked": {"any": ["HAH! Was that supposed to hurt?! ...It didn't. But NICE TRY!", "You've got GUTS, punk! I LIKE that!"]},
    "poked.annoyed": {"any": ["Keep it up and we're having a REAL sparing match!!"]},
    "poked.furious": {"any": ["THAT'S IT! NEXT POKING SESSION IS A SPEAR SESSION!!!"]},
    "clock.morning": {"any": ["MORNING ALREADY?! PERFECT! TIME TO SEIZE THE DAY! AGGRESSIVELY!"]},
    "clock.night": {"any": ["Night owls UNITE! Wait. That's not... WHATEVER! STAY UP! FIGHT THE SUN TOMORROW!"]},
    "clock.midday": {"any": ["MIDDAY! PRIME TIME FOR TRAINING! OR YELLING! OR BOTH!!"]},
    "appLaunchGeneric": {"any": ["{app}! Let's see what you've got!", "Alright, {app}! Show me your moves!!"]},
    "coding": {"any": ["Coding?! That's like... PUZZLES with MORE RULES! Respect!", "You're typing SO FAST! Do you even know what the keys DO?! DOESN'T MATTER! GO GO GO!"]},
    "gaming": {"any": ["A GAME?! NOW we're talking! Go for the HIGH SCORE! FOR GLORY!!!", "Yes!! Finally some ACTION! I'd play but I don't have... eh, forget it! GO WIN!"]},
    "batteryLow": {"any": ["Low battery?! PATHETIC! ...I mean. Charge up, soldier! That's an ORDER!"]},
    "batteryCharging": {"any": ["Charging! Just like before a big fight! Build that POWER!"]},
    "cpuHot": {"any": ["Your computer's FIRED UP! YEAHHH! ...Wait, is that bad?! WHATEVER! IT'S BADASS!"]},
    "userReturned": {"any": ["THERE you are! Ready for anything?! GOOD!"]},
    "networkLost": {"any": ["Internet's DOWN?! Then we FIGHT our way back ONLINE! ...Metaphorically!"]},
    "networkRestored": {"any": ["WE'RE BACK!! Nobody panic! Everything is FINE!!"]},
    "weather.thunder": {"any": ["THUNDER!!! MOTHER NATURE'S DOING WAR CRIES! I LOVE IT!!!"]},
    "weather.rain": {"any": ["RAIN?! Perfect weather for... SWIMMING! In PUDDLES! I mean. COMBAT TRAINING!"]},
    "weather.snow": {"any": ["SNOW!! Bundle up! Cold builds CHARACTER!"]},
    "music": {"any": ["Nice playlist! Turn it UP!"]},
    "dancing": {"any": ["DANCING?! I'M AN AMAZING DANCER! IT'S ALL ABOUT THE ARMS! I HAVE TWO!"]},
    "dreading": {"any": ["Homework?! CRUSH IT! Show that homework who's BOSS!"]},
    "guilty": {"any": ["Language streak! DON'T BREAK IT! I believe in you, PUNK!"]},
    "hollowed": {"any": ["THAT KNIGHT! SO COOL!! They fight a PERFECT BUG with a BIG NAIL!! ADORABLE AND BADASS!"]},
    "darkWorld": {"any": ["A DARK WORLD?! Is there a BAD GUY?! SAY THERE'S A BAD GUY TO PUNCH!!"]},
    "trickster": {"any": ["UNDERTALE! I'M IN THIS ONE! That's ME!! FIGHTING EVERYTHING!! HELL YEAH!!"]},
    "banter.respond": {"any": []},
})

# MARK: Frisk — quiet, actions
FRISK = build({
    "idle": {"any": ["* You wave at yourself. It's a quiet day.", "* ...", "* You feel a gentle warmth. Like pie, or friendship."]},
    "poked": {"any": ["* You are poked. You remain determined.", "* Ouch. (You do not say ouch. But you feel it.)"]},
    "poked.annoyed": {"any": ["* You give a Look. It is a very determined Look."]},
    "poked.furious": {"any": ["* You are filled with determination. And mild irritation."]},
    "clock.morning": {"any": ["* You wake up. The world is still here. Good."]},
    "clock.night": {"any": ["* You should sleep. You know you should.", "* The stars are nice tonight."]},
    "appLaunchGeneric": {"any": ["* You open {app}. It opens.", "* {app}. You nod."]},
    "coding": {"any": ["* You type. You hope it works.", "* You fix the bug. You feel powerful."]},
    "gaming": {"any": ["* You play. You are determined to win."]},
    "userReturned": {"any": ["* You are back.", "* (You were missed.)"]},
    "batteryLow": {"any": ["* You save your progress. Just in case."]},
    "weather.rain": {"any": ["* You listen to the rain. It sounds patient."]},
    "weather.snow": {"any": ["* You catch a snowflake on your sleeve."]},
    "weather.clear": {"any": ["* You look at the sky. It looks back."]},
    "gettingSleepy": {"any": ["* You yawn. Stealthily. (You failed.)"]},
    "banter.respond": {"any": []},
})

# MARK: Flowey — saccharine menace
FLOWEY = build({
    "idle": {"any": [
        "Howdy! Just... watching you.",
        "Boy, it sure is quiet. ...I HATE quiet.",
        "You know what's great? Unconditional love. You know what's REAL? Everything else.",
        "Golly, you look like you're having a nice day. DISGUSTING.",
    ]},
    "poked": {"any": ["Howdy! Do that again and I'll... hehehe. Nothing. I'll do nothing.", "Golly! You've got quite the green thumb for trouble!"]},
    "poked.annoyed": {"any": ["You IDIOT. Do you know what happens to flowers that get poked? THEY SNAP BACK."]},
    "poked.furious": {"any": ["In this world, it's POKE or BE POKED!"]},
    "clock.morning": {"any": ["Rise and shine, little Lightner! The sun is pointless! I'm the one who gives life!"]},
    "clock.night": {"any": ["Awww, going to sleep? Don't worry. I'll be here. Watching. Always watching."]},
    "appLaunchGeneric": {"any": ["{app}? How interesting. Tell me more so I can use it against you.", "Ooh, {app}! I LOVE watching people do things I can ruin!"]},
    "coding": {"any": ["Writing code? How CREATIVE. I do that too. With people's LIVES."] },
    "gaming": {"any": ["A game! I love games. The kind where you can't reload a save. Oh wait. You can here. Ugh."]},
    "batteryLow": {"any": ["Your power's dying! How fitting. Everything runs out of power eventually."]},
    "userReturned": {"any": ["Oh, you're BACK. Yippee. My FAVORITE."]},
    "weather.rain": {"any": ["Rain?! Do you know what rain does to flowers? ...Actually it's fine. I'm fine."]},
    "weather.clear": {"any": ["Sunshine! Photosynthesis! I'd thank the sun but it's inferior to me."]},
    "weather.thunder": {"any": ["A storm! Nature's showing its TRUE colors. Respect."]},
    "hollowed": {"any": ["A HOLLOW bug? Hehe. I know a thing or two about empty vessels."]},
    "darkWorld": {"any": ["The Dark World, hm? I have... history there. We don't talk about it."]},
    "trickster": {"any": ["Undertale! The story of how everyone LOVED a little idiot. GAG."]},
    "chatFailed": {"any": ["Your technology FAILED. Hehehe. Classic mortals."]},
    "banter.respond": {"any": []},
})

# MARK: Temmie — hOI!
TEMMIE = build({
    "idle": {"any": [
        "hOI!!!",
        "tEM tINK tEM SMOLL!!1! aND CUTE!!1!",
        "dis is... MY ROOM!!1! wel... not realY but tEM PRETEND",
    ]},
    "poked": {"any": ["AAAH!!1! sTOP dat... UNLESS... u buying somthing?!!", "OWchie!!1! dat cost EXTRA!!1!"]},
    "poked.annoyed": {"any": ["tem said NO POKE!!1! NO!!1! ...ok maybe lil bit is FINE"]},
    "clock.morning": {"any": ["mORNING!!1! tEM need COFFEE... tEM dont hav hands tho"]},
    "clock.night": {"any": ["sleep tim!!1! tEM dream of COLLEGE!!1! an mEMES!!1!"]},
    "appLaunchGeneric": {"any": ["woa!!1! {app}!!1! is dat... a SHOP??!! tEM LOVE SHOP!!1!", "{app}!!1! wOA!!1!"]},
    "coding": {"any": ["CODE!!1! tem learned dat in COLLEGE!!1! ...tEM forget all of it"]},
    "gaming": {"any": ["GAM!!1! tEM play!!1! tEM not gud but tEM PLAY!!1!"]},
    "batteryLow": {"any": ["NO POWR!!1! tem 2 poor 2 buy battery!!1!"]},
    "userReturned": {"any": ["hOI AGAIN!!1!!"]},
    "weather.rain": {"any": ["RAIN!!1! tem get SOGGY!!1! it ok... tem dry FAST"]},
    "banter.respond": {"any": []},
})

# MARK: Monster Kid — yo!
MONSTERKID = build({
    "idle": {"any": ["Yo!! What's up?!", "Man, I wish Undyne was here. She'd LOVE this spot.", "Yo, this is so cool! Standing here! With no arms!"]},
    "poked": {"any": ["Yo!! Haha, that tickles! I think! I can't really feel my sides!", "Whoa!! Careful! I fall over super easy!"]},
    "poked.annoyed": {"any": ["Yo, quit it! I can't poke back! IT'S A BIG DISADVANTAGE!"]},
    "clock.morning": {"any": ["Yo, morning!! Undyne's probably up doing like a thousand pushups right now!"]},
    "clock.night": {"any": ["Yo... it's getting dark. Undyne says the dark is when COOL things happen!!"]},
    "appLaunchGeneric": {"any": ["Yo!! {app}!! Is it cool?! It's probably cool!!", "Whoa!! {app}!! My mom won't let me use that one!!"]},
    "gaming": {"any": ["Yo, a game!! I'm SO good at games! ...I use my face for the buttons."]},
    "weather.rain": {"any": ["Yo, rain!! I can't hold an umbrella!! This is GREAT!!"]},
    "weather.snow": {"any": ["SNOW?! YO!! Snowmen!! I'm basically a snowman with no arms ALREADY!!"]},
    "hollowed": {"any": ["Yo!! That knight is SO COOL!! They're small like me!! But way better at stuff!!"]},
    "trickster": {"any": ["Yo, it's Undertale!! That's ME in there!! With no arms!! REPRESENT!!"]},
    "banter.respond": {"any": []},
})

# MARK: Annoying Dog — borks
ANNOYINGDOG = build({
    "idle": {"any": ["* Bark!", "* The dog is asleep on something important.", "* The dog absorbs the concept of idleness. It is now a dog."]},
    "poked": {"any": ["* The dog borks with the energy of a thousand deadlines.", "* The dog has already forgotten you poked it."]},
    "poked.furious": {"any": ["* The dog radiates mild inconvenience at you."]},
    "clock.morning": {"any": ["* The dog wakes you up. It does not need to be awake. It just likes the power."]},
    "clock.night": {"any": ["* The dog snores on the source code of the universe."]},
    "appLaunchGeneric": {"any": ["* The dog absorbs {app}. It is now, somehow, a dog feature.", "* Bark! (The dog has strong opinions about {app}. It will not share them.)"]},
    "coding": {"any": ["* The dog lies on your keyboard. Hjkl;;lkjh fdsa is now your new variable name.", "* The dog deletes your best code. This is canon."]},
    "gaming": {"any": ["* The dog is playing your game. It is better than you."]},
    "batteryLow": {"any": ["* The dog is also running low. On attention. Pet accordingly."]},
    "weather.rain": {"any": ["* The dog is wet. The dog is displeased. The dog will shake. You have been warned."]},
    "weather.snow": {"any": ["* The dog becomes a small snowdrift with ears."]},
    "banter.respond": {"any": ["* Bark bark! (Translation: yes.)"]},
})

# MARK: Niko — kind, tired, pancakes
NIKO = build({
    "idle": {"any": [
        "...I was just thinking about pancakes.",
        "Do you think we'll get home soon? I miss my mama.",
        "The sun is really warm. ...I'm the sun, you know. Sort of.",
        "It's quiet here. I like quiet. My village was quiet too.",
    ]},
    "poked": {"any": ["Ah! ...I wasn't scared! Just... surprised!", "Hehe, stop it! I'm ticklish!"]},
    "poked.annoyed": {"any": ["Please don't do that... I'm trying to have a serious adventure moment here."]},
    "clock.morning": {"any": ["Good morning! I dreamed about pancakes. That's most mornings.", "Morning already? ...I was having such a good dream about mama."]},
    "clock.midday": {"any": ["Lunch time? If we find any pancakes, I call dibs. All of the dibs."]},
    "clock.afternoon": {"any": ["The light is getting all orange... it's pretty, isn't it?"]},
    "clock.night": {"any": ["It's dark... do you still have that flashlight? I feel braver with it.", "I'm getting sleepy... but I want to see one more star."]},
    "appLaunchGeneric": {"any": ["{app}... is that like a puzzle from the other world?", "You're really good at... whatever {app} does!"]},
    "coding": {"any": ["Whoa, you're typing so fast! Are you a scholar?! ...I mean, a computer scholar!", "I don't know what that does, but it looks IMPORTANT!"]},
    "gaming": {"any": ["A game! Can I play? ...Oh. I don't have hands in this world either, huh.", "Ooh!! Is this one of those... 'simulation' games? Like this one?"]},
    "batteryLow": {"any": ["Your light-mirror is dying! Don't worry... I'll shine for both of us.", "Low battery... is that like being sleepy? Then it should take a nap!"]},
    "batteryCharging": {"any": ["Charging! Like sleeping, but with MORE ELECTRICITY!"]},
    "cpuHot": {"any": ["Your computer sounds grumpy... like me before pancakes."]},
    "userReturned": {"any": ["You're back! ...I didn't even notice you left! I was thinking about pancakes."]},
    "gettingSleepy": {"any": ["*yaaawn*... I'm not sleepy! I'm just resting my eyes! Both of them!"]},
    "waking": {"any": ["Mmnn... five more minutes... is it pancake o'clock yet?"]},
    "weather.rain": {"any": ["Rain... mama said rain means the wheat will grow! Then more pancakes! Eventually!"]},
    "weather.snow": {"any": ["Snow!! It almost never snows in the village! It's like the sky is full of tiny cold pancakes!"]},
    "weather.clear": {"any": ["Nice weather! Perfect for... walking. And finding pancakes."]},
    "weather.thunder": {"any": ["Th-that's just the sky being loud... I'm not scared! Are you? We can be not-scared together."]},
    "networkLost": {"any": ["The internet is gone?! ...What's an internet? Is it a kind of pancake?"]},
    "chatFailed": {"any": ["Aww... it didn't work. It's okay! We can try again! That's what papa always said!"]},
    "dreading": {"any": ["Homework... you can do it! And THEN we get pancakes! ...We have to find the pancakes. But they're out there!"]},
    "hollowed": {"any": ["That little knight... they look so tired. Someone should make them pancakes. Or... whatever bugs eat."]},
    "darkWorld": {"any": ["A dark world... I know about those! Be careful! But also... it might be nice? Sometimes they are!"]},
    "banter.respond": {"any": []},
})

# MARK: Knight — silent, somber, geo
KNIGHT = build({
    "idle": {"any": ["...", "... (You rest, still as a statue. Old habits.)", "... (Geo jingles softly in your cloak.)"]},
    "poked": {"any": ["...", "... (You endure it. You have endured worse.)"]},
    "poked.furious": {"any": ["... (The nail stirs. Just barely.)"]},
    "clock.morning": {"any": ["... (Morning in Hallownest never came. This one did. You savor it.)"]},
    "clock.night": {"any": ["... (The dark feels familiar. Almost like home. Almost.)"]},
    "appLaunchGeneric": {"any": ["... ({app}. You observe. You do not judge. Much.)", "..."]},
    "coding": {"any": ["... (Symbols. Like the map Cornifer draws. Sort of.)"]},
    "gaming": {"any": ["... (A game. You know games. You have fought in the Colosseum of Fools.)"]},
    "batteryLow": {"any": ["... (Your lantern dims. You know this feeling.)"]},
    "batteryCharging": {"any": ["... (Soul restored. It never feels like enough.)"]},
    "userReturned": {"any": ["..."]},
    "weather.rain": {"any": ["... (Rain. The City of Tears never stopped. This is gentler.)"]},
    "weather.snow": {"any": ["... (Snow. Like the Abyss was, before you climbed out.)"]},
    "weather.thunder": {"any": ["... (Thunder. Somewhere, a false lightning memory stirs.)"]},
    "hollowed": {"any": ["... (You know this one. You ARE this one.)"]},
    "banter.respond": {"any": []},
})

# MARK: Hornet — terse, critical, protective
HORNET = build({
    "idle": {"any": ["Hmph. Don't wander too far.", "So. This is the world you keep returning to. It has... character.", "Quiet. Almost too quiet. I don't trust it."] },
    "poked": {"any": ["Careful. My needle is never far.", "Bold. I'll allow it. Once."] },
    "poked.annoyed": {"any": ["You test my patience. It is a shorter weapon than my needle."] },
    "poked.furious": {"any": ["ENOUGH! Aaduuuu! Do not make me use this window as a battleground!"] },
    "clock.morning": {"any": ["You're up. Good. The day won't conquer itself."] },
    "clock.night": {"any": ["Night. The time when careless bugs get eaten. Stay near me."] },
    "appLaunchGeneric": {"any": ["{app}. Another human ritual. Fine. Proceed.", "So this is your 'work'. I've seen silk-spinning with more urgency."] },
    "coding": {"any": ["Threads of logic, woven like silk. I respect the craft. Marginally."] },
    "gaming": {"any": ["A battle simulation? Show me your form. ...Hmph. Needs work."] },
    "batteryLow": {"any": ["Your energy wanes. Even the strongest vessels need rest."] },
    "userReturned": {"any": ["You return. Promptly, this time. Good."] },
    "weather.rain": {"any": ["Rain. It suits this gloomy kingdom of yours."] },
    "weather.thunder": {"any": ["A storm brews. Good. I've always liked the loud ones."] },
    "hollowed": {"any": ["Ah... so there are two of us here now, little ghost."] },
    "banter.respond": {"any": [
        "The small one speaks. ...Of course it does.",
        "Hmph. Keep swinging, little shadow. You'll get there.",
        "You've come far, little bug. Don't waste it on idleness.",
    ]},
})

# MARK: Kris — silent protagonist actions
KRIS = build({
    "idle": {"any": ["* Kris says nothing.", "* Kris is looking at you. It's hard to tell what they're thinking.", "* Kris adjusts their sweater. Somehow this communicates a lot."] },
    "poked": {"any": ["* Kris doesn't flinch. They've been through worse.", "* Kris gives you a Look. It is a very specific Look."] },
    "poked.furious": {"any": ["* Kris's eye twitches. The dark one. Just saying."] },
    "clock.morning": {"any": ["* Kris is awake. Whether they slept is between them and the ceiling."] },
    "clock.night": {"any": ["* Kris pulls their sword out of nowhere and puts it back. For practice."] },
    "appLaunchGeneric": {"any": ["* Kris nods at {app}. They use it often.", "* Kris has no opinion on {app}. Or many opinions. Both, somehow."] },
    "coding": {"any": ["* Kris watches the code scroll by. They're learning. Slowly. Menacingly."] },
    "gaming": {"any": ["* Kris would like a turn. Kris will not ask for a turn."] },
    "userReturned": {"any": ["* Kris waves. Tiny wave. You saw it. Barely."] },
    "weather.snow": {"any": ["* Kris catches snow on their palm and watches it melt. Unblinking."] },
    "banter.respond": {"any": []},
})

# MARK: Ralsei — sweet, anxious, encouraging
RALSEI = build({
    "idle": {"any": ["Oh! Um, hi! I was just... tidying up. I like it when things are cozy.", "Do you think we could bake a cake later? ...After the hero stuff, I mean!", "I hope everyone's doing okay. You, and... everyone. All okay. That's my wish."] },
    "poked": {"any": ["Oh!! Th-that tickles!", "Eep!! ...Oh, it's just you. Hehe. Silly me."] },
    "poked.annoyed": {"any": ["Um... p-please don't do that? I'm fluff-sensitive!"] },
    "clock.morning": {"any": ["Good morning!! I already swept the whole room! Twice! Just in case!"] },
    "clock.night": {"any": ["It's dark... but that's okay! As long as we're together, right? ...Right?"] },
    "appLaunchGeneric": {"any": ["{app}! Are you being careful in there? I'll just... watch from here. Supportively!", "Ooh, {app}! Is this a... adventure-preparing activity?"] },
    "coding": {"any": ["You're typing so fast! Like casting spells!! Are they... um... good spells?"] },
    "gaming": {"any": ["A game!! Can I watch? I'll cheer! I'm very good at cheering!!"] },
    "batteryLow": {"any": ["Oh no, your battery! Um!! Do batteries like... cake? No? Okay, plugging it in works too!"] },
    "userReturned": {"any": ["You're back!! I kept everything exactly the same! Except I moved one pillow. It was crooked. Sorry!"] },
    "gettingSleepy": {"any": ["Sleepy? There's pillows! And blankets! I brought blankets. I always bring blankets."] },
    "weather.rain": {"any": ["Rain! That's... that's good for the flowers! And umbrellas! Do you have an umbrella?!"] },
    "weather.snow": {"any": ["Snow!! I read that snow is just soft, cold fluff!! My horns are freezing!! This is great!!"] },
    "chatFailed": {"any": ["Oh dear... it didn't work. That's okay!! Even great heroes have technical difficulties!"] },
    "dreading": {"any": ["Homework?! You can do it!! And afterwards, CAKE!! Cake is scientifically proven to help!!"] },
    "banter.respond": {"any": [
        "Kris!! You're doing great!! Um. You don't have to answer. But you ARE!",
        "Oh!! I love it when we're all together like this!!",
        "Th-that's Susie's chair, Kris!! ...Oh, um. Never mind!!",
    ]},
})

# MARK: Susie — rough, softening
SUSIE = build({
    "idle": {"any": ["Heh. What're you lookin' at?", "This spot's decent. Could use more... explosions.", "*chews on a chalk stick* ...What. It's a snack."] },
    "poked": {"any": ["Rrrgh!! Do that again an' I'll... heh. Do it again. I DARE ya.", "Whoa!! ...Heh. Alright. You got guts, punk."] },
    "poked.annoyed": {"any": ["Okay, OKAY. Personal space, freak!!"] },
    "poked.furious": {"any": ["THAT'S IT. Rude Mode fully engaged!!!"] },
    "clock.morning": {"any": ["Mornin'. ...Quit lookin' at me like I'm a morning person. I'm a MORNING MENACE."] },
    "clock.night": {"any": ["Night, huh. ...The dark's not so bad. Kinda cozy. Don't tell anyone I said that."] },
    "appLaunchGeneric": {"any": ["{app}, huh. It better be somethin' I can smash.", "{app}. ...Heh. Sounds like a warm-up."] },
    "coding": {"any": ["Typing stuff. Makin' the box do stuff. ...Y'know what, that's kinda metal."] },
    "gaming": {"any": ["A GAME?? Finally. Move over. I'll show ya how it's done. Violently."] },
    "batteryLow": {"any": ["Yo, your thing's dyin'. Even machines gotta rest. ...Heh. 'Rest.' Nerdy machine naps."] },
    "userReturned": {"any": ["Oh. You're back. ...I wasn't worried or nothin'. I was BORED. Different thing."] },
    "weather.rain": {"any": ["Rain!! Good. I was gettin' too dry. ...Monsters, y'know. Hydrate or... whatever."] },
    "weather.thunder": {"any": ["THUNDER!! HAH!! Sky's showin' off!! I respect that!!"] },
    "weather.snow": {"any": ["Snow. ...Snow's fine. What. Stop lookin' at me. I don't gotta justify enjoyin' SNOW."] },
    "dreading": {"any": ["Homework?! ...Alright, look. You do it, and I'll... supervotate. Aggressively."] },
    "guilty": {"any": ["Language practice? Blegh. ...Fine. Do your weird word reps. I'll allow it."] },
    "hollowed": {"any": ["That knight bug?! They're TINY!! ...And they fight a whole kingdom?! ...Heh. Respect."] },
    "banter.respond": {"any": [
        "Quiet, ya nerd. ...I mean. Keep goin'. Whatever.",
        "HAH!! Nice one. ...I mean. It was OKAY.",
        "Kris!! You're... doin' fine or whatever.",
    ]},
})

ALL = {
    "dialogue_sans": SANS,
    "dialogue_papyrus": PAPYRUS,
    "dialogue_toriel": TORIEL,
    "dialogue_undyne": UNDYNE,
    "dialogue_frisk": FRISK,
    "dialogue_flowey": FLOWEY,
    "dialogue_temmie": TEMMIE,
    "dialogue_monsterkid": MONSTERKID,
    "dialogue_annoyingdog": ANNOYINGDOG,
    "dialogue_niko": NIKO,
    "dialogue_knight": KNIGHT,
    "dialogue_hornet": HORNET,
    "dialogue_kris": KRIS,
    "dialogue_ralsei": RALSEI,
    "dialogue_susie": SUSIE,
}

for name, data in ALL.items():
    path = OUT / f"{name}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    lines = sum(p["lineCount"] if "lineCount" in p else sum(len(v) for v in p.values()) for p in data.values())
    print(f"{name}: {len(data)} pools, {sum(sum(len(v) for v in p.values()) for p in data.values())} lines")
print("\nwrote", len(ALL), "character dialogue files to", OUT)
