import fs from "fs"

async function translateMissing(filePath) {
  const data = JSON.parse(fs.readFileSync(filePath, "utf8"))
  let updateCount = 0

  for (const [key, value] of Object.entries(data)) {
    if (key === value) {
      try {
        data[key] = await translate(value, "FR", "EN")
        console.log(`> Translated "${value}" to "${data[key]}"`)
        fs.writeFileSync(filePath, JSON.stringify(data, null, "  "), "utf8")
        await wait(1000)
        updateCount++
      } catch (error) {
        console.log(`> Error translating "${value}": ${error.message}`)
      }
    }
  }

  console.log(`> ${updateCount} bad translations updated`)
}

async function translate(text, source_lang, target_lang) {
  const params = {
    text: [text],
    source_lang,
    target_lang,
  }

  const response = await fetch("https://api-free.deepl.com/v2/translate", {
    method: "POST",
    headers: {
      Authorization: `DeepL-Auth-Key ${process.env.DEEPL_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  })

  if (!response.ok) {
    throw new Error(
      `DeepL API error: ${response.status} ${response.statusText}`
    )
  }

  const data = await response.json()
  return data.translations[0].text
}

function wait(time) {
  return new Promise((resolve) => setTimeout(resolve, time))
}

translateMissing("public/locales/en/translation.json")
