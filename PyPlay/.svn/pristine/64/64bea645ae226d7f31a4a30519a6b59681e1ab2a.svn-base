
#include <algorithm>
#include <string>
#include <locale>

#include <map>
#include <vector>

#include "WAVFile.h"
#include "Features.h"

#pragma once

struct CMUPhoneme {
	enum Type{ Vowel, Stop, Affricate, Fricative, Aspirate, 
		Liquid, Nasal, Semivowel, Unknown };
	static const std::string type_names[];

	static std::string type_to_string(Type t) {
		return type_names[t];
	}

	static Type string_to_type(const std::string t) {
		return Type(std::find(type_names, type_names+7, t) -
			type_names);
	}

	CMUPhoneme() : variant(0), type(Unknown){}
	CMUPhoneme(const std::string& name_, const std::string& type_) :
		name(name_), type(string_to_type(type_)),
		variant( std::isdigit(name_[name_.length()-1], std::locale())?
			name_[name_.length()-1] - '0': 0 ){}

	std::string name;
	unsigned char variant;
	Type type;
};

bool operator<(const CMUPhoneme& lhs, const CMUPhoneme& rhs);
bool operator==(const CMUPhoneme& lhs, const CMUPhoneme& rhs);
bool operator==(const CMUPhoneme& lhs, const std::string& rhs);

class CMUDictionaryData {
	std::vector< CMUPhoneme > _phonemes;

	typedef std::map< std::string, std::vector<CMUPhoneme> > Dictionary;
	Dictionary _dictionary;

public:
	CMUDictionaryData(const std::string& phones, const std::string& symbols,
		const std::string& dictionary);

	const std::vector<CMUPhoneme>& phonemes() { return _phonemes; }

	bool has_word(const std::string& word) const {
		return _dictionary.count(word) != 0;
	}
	const std::vector<CMUPhoneme>& operator[](const std::string& word) const {
		return _dictionary.at(word);
	}
};

struct VoxforgePrompt {
	std::string speaker, prompt, wavfile;
	std::vector< CMUPhoneme > phonemes;

	VoxforgePrompt(const std::string& filename, 
		const std::vector<std::string>& prompt,
		const CMUDictionaryData& dict);
};

class VoxforgeData {
    std::vector< VoxforgePrompt > _prompts;
	void load_prompts(const std::string& path, const CMUDictionaryData& dict);

public:
	VoxforgeData(const std::string& root, const CMUDictionaryData& dict);
	const std::vector< VoxforgePrompt >& prompts() { return _prompts; }
};

