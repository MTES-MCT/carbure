import fs from "fs"

async function translateMissing(translationPath, sourcePath, context) {
  const translation = JSON.parse(fs.readFileSync(translationPath, "utf8"))
  const source = JSON.parse(fs.readFileSync(sourcePath, "utf8"))

  const keys = Object.keys(translation)
  const missingKeys = keys.filter(
    (key) => key.includes(" ") && key.includes(translation[key])
  )

  console.log(
    `> Found ${missingKeys.length}/${keys.length} missing translations`
  )

  for (let i = 0; i < missingKeys.length; i++) {
    const key = missingKeys[i]
    const value = source[key]
    try {
      translation[key] = await translate(value, "FR", "EN", context)
      console.log(
        `> (${i + 1}/${missingKeys.length}) Translated "${value}" to "${translation[key]}"`
      )
      fs.writeFileSync(
        translationPath,
        JSON.stringify(translation, null, "  "),
        "utf8"
      )
      await wait(1000)
    } catch (error) {
      console.log(`> Error translating "${value}": ${error.message}`)
    }
  }

  console.log(`> Translations updated successfully`)
}

async function translate(text, source_lang, target_lang, context) {
  const params = {
    text: [text],
    source_lang,
    target_lang,
  }

  if (context) {
    params.context = context
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

// Parse command line arguments
if (process.env.DEEPL_API_KEY) {
  translateMissing(
    "public/locales/en/translation.json",
    "public/locales/fr/translation.json",
    process.argv[2]
  )
} else {
  throw new Error("DEEPL_API_KEY not found in env")
}
