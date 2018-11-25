# coding: UTF-8
from structure.nodes import Paragraph, Relation


class PartitionPtrParser:
    def __init__(self, model):
        self.model = model

    def parse(self, edus):
        # TODO implement beam search
        session = self.model.init_session(edus)
        while not session.terminate():
            split_scores, nucs_score, state = self.model(session)
            split = split_scores.argmax()
            nuclear_id = nucs_score[split].argmax()
            nuclear = self.model.nuc_label.id2label[nuclear_id]
            session = session.forward(split_scores, state, split, nuclear)
        # build tree by splits (left, split, right)
        root_relation = self.build_tree(edus, session.splits[:], session.nuclears[:])
        discourse = Paragraph([root_relation])
        return discourse

    def build_tree(self, edus, splits, nuclears):
        left, split, right = splits.pop(0)
        nuclear = nuclears.pop(0)
        if split - left == 1:
            left_node = edus[left]
        else:
            left_node = self.build_tree(edus, splits, nuclears)

        if right - split == 1:
            right_node = edus[split]
        else:
            right_node = self.build_tree(edus, splits, nuclears)

        relation = Relation([left_node, right_node], nuclear=nuclear)
        return relation
