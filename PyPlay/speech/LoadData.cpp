
#include <algorithm>
#include <string>
#include <locale>
#include <fstream>
#include <sstream>

#include <boost/filesystem.hpp>

#include "LoadData.h"

using namespace boost::filesystem;
const std::string CMUPhoneme::type_names[] = { "vowel", "stop", 
	"affricate", "fricative", "aspirate", "liquid", "nasal", "semivowel" };

bool operator<(const CMUPhoneme& lhs, const CMUPhoneme& rhs) {
	return lhs.name < rhs.name;
}

bool operator==(const CMUPhoneme& lhs, const CMUPhoneme& rhs) {
	return lhs.name == rhs.name;
}

bool operator==(const CMUPhoneme& lhs, const std::string& rhs) {
	return lhs.name == rhs;
}

CMUDictionaryData::CMUDictionaryData(const std::string& phones,
	const std::string& symbols,
	const std::string& dictionary) {

	std::map<std::string, std::string> types;
	std::string linedata;

	{
		std::ifstream file(phones);
		if (!file.is_open()) {
			std::cout << "Failed to open phones file." << std::endl;
			return;
		}
		while (std::getline(file, linedata)) {
			std::stringstream line(linedata);
			std::string name, type;
			if (!(line >> name >> type)) break;
			types[name] = type;
		}
	}

	{
		std::ifstream file(symbols);
		if (!file.is_open()) {
			std::cout << "Failed to open symbols file." << std::endl;
			return;
		}

		std::getline(file, linedata);
		std::string base_phone = linedata;
		bool has_variants = false;

		while (std::getline(file, linedata)) {
			if (std::isdigit(linedata[linedata.length()-1], std::locale())) {
				has_variants = true;
				_phonemes.emplace_back(linedata, types[base_phone]);
			}
			else {
				if (!has_variants)
					_phonemes.emplace_back(base_phone, types[base_phone]);
				base_phone = linedata;
				has_variants = false;
			}
		}

		if (!has_variants)
			_phonemes.emplace_back(base_phone, types[base_phone]);
	}

	std::ifstream file(dictionary);
	if (!file.is_open()) {
		std::cout << "Failed to open dictionary file." << std::endl;
		return;
	}
	while (std::getline(file, linedata)) {
		if (linedata[0] == ';') continue;
		std::stringstream line(linedata);

		std::string word;
		if (!(line >> word)) break;

		std::istream_iterator<std::string> begin(line), end;
		std::vector<CMUPhoneme> phonemes;
		std::transform(begin, end, std::back_inserter(phonemes),
			[this](const std::string p){
			return *std::find(_phonemes.begin(), _phonemes.end(), p);
		});

		_dictionary[word] = phonemes;
	}
}

VoxforgePrompt::VoxforgePrompt(const std::string& filename,
	const std::vector< std::string >& words, 
	const CMUDictionaryData& dict) :
	wavfile(filename) {
	std::stringstream full_prompt;
	std::copy(words.begin(), words.end(),
		std::ostream_iterator<std::string>(full_prompt, " "));
	prompt = full_prompt.str();

	for (auto i = words.begin(); i != words.end(); ++i) {
		auto word_phonemes = dict[*i];
		phonemes.insert(phonemes.end(),
			word_phonemes.begin(), word_phonemes.end());
	}
}

void VoxforgeData::load_prompts(const std::string& p, 
	const CMUDictionaryData& dict) {

    path prompts = path(p) / "etc" / "PROMPTS";
    if( !is_regular_file( prompts ) ) {
        std::cout << "Voxforge directory has no prompts." << std::endl;
        return;
    }

    std::ifstream pfile( prompts.c_str() );
	std::string linedata;
    while( std::getline(pfile, linedata)) {
        std::stringstream line( linedata );
        std::string wavfile;
		if (!(line >> wavfile))	break;

		path wavpath(wavfile);
		path newpath = p / "wav" / wavpath.filename();
		newpath.replace_extension(".wav");

        std::istream_iterator<std::string> begin( line ), end;
        std::vector< std::string > words( begin, end );
		if (!std::all_of(words.begin(), words.end(),
			std::bind(&CMUDictionaryData::has_word,
			std::cref(dict), std::placeholders::_1)))
			continue;

		_prompts.emplace_back(newpath.generic_string(),
			words, dict);
    }

}

VoxforgeData::VoxforgeData( const std::string& root, 
	const CMUDictionaryData& dict ) {

    path p = root;
    if( !is_directory( p ) ) {
        std::cout << "Voxforge root is not a directory." << std::endl;
        return;
    }

    std::vector< path > paths;
    std::copy( directory_iterator(p), directory_iterator(), 
        back_inserter( paths ) );
    std::sort( paths.begin(), paths.end() );

	size_t max_read = 1, c = 0;
    for( auto i = paths.begin(); i != paths.end() && c < max_read; ++i, ++c ) {
		load_prompts(i->generic_string(), dict);
    }

}

