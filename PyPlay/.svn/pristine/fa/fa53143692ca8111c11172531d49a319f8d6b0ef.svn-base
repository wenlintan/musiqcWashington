
#include <iostream>
#include <thread>

#include "WAVFile.h"
#include "LoadData.h"

#include "GMM.h"
#include "HMM.h"

struct Phone {
	double transitions[3];
	GMM gmms[3];
};

struct DecisionTree {

};

struct EMTask {
	typedef std::tuple<CMUPhoneme, CMUPhoneme, CMUPhoneme> Neighborhood;
	typedef std::map< CMUPhoneme, Phone > PhoneMap;

	const VoxforgePrompt& prompt;
	PhoneMap& phones;

	ContinuousForwardGMMHMM hmm;
	MFCC mfcc;	

	EMTask(PhoneMap& phones_, VoxforgePrompt& prompt_) :
		mfcc(MFCCOptions{
			25.0, 15.0, 23, 13, 16000, 20, 7800, 22., 
			true, true, false, false }),
		phones(phones_), prompt(prompt_) {}

	void operator()() {
		WaveFile wave(prompt.wavfile);
		MFCC::MatrixType features = mfcc(wave);

		std::vector< ForwardGMMState > states;
		for (auto i : prompt.phonemes) for (auto j : { 0, 1, 2 }) {
			states.push_back(ForwardGMMState{ phones[i].transitions[j],
				phones[i].gmms[j] });
		}

		hmm.forward_backward(states, features);
		for (auto i : features) {

		}
	}
};

int main(int argc, char** argv) {
	//std::string filename( "C:\\Users\\Crazed\\Desktop\\SVN\\Data\\speech\\voxforge-snapshot\\1028-20100710-hne\\wav\\ar-01.wav" );
	//WaveFile file( filename );

	std::cout << sizeof(Phone) << std::endl;
	return 0;

	MFCC mfcc(MFCCOptions{
		25.0, 15.0, 23, 13, 16000, 20, 7800, 22., 
		true, true, false, false });
	CMUDictionaryData dict(
		"C:\\Users\\Crazed\\Desktop\\SVN\\Data\\dictionary\\cmudict.0.7a.phones",
		"C:\\Users\\Crazed\\Desktop\\SVN\\Data\\dictionary\\cmudict.0.7a.symbols",
		"C:\\Users\\Crazed\\Desktop\\SVN\\Data\\dictionary\\cmudict.0.7a");
	VoxforgeData prompts(
		"C:\\Users\\Crazed\\Desktop\\SVN\\Data\\speech\\voxforge-snapshot\\",
		dict);
	
	EMTask::PhoneMap phones;

	for (auto i: dict.phonemes()) {
		phones.insert( std::make_pair( i, Phone{ { 0.3, 0.3, 0.3 }, 
			{ GMM(8, mfcc.nfeatures()), GMM(8, mfcc.nfeatures()), 
				GMM(8, mfcc.nfeatures()) } } ));
	}

	std::vector<std::thread> threads;
	for (auto i = 0u; i < std::thread::hardware_concurrency(); ++i) {
		threads.emplace_back(EMThread(phones, prompts.prompts()));
	}

	for (auto& i : threads) {
		i.join();
	}

	std::cout << "Yay." << std::endl;
    return 0;
}

